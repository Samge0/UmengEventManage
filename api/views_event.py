#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/3 下午4:29
# @Author  : Samge
import hashlib
import json
import os
import time

from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from . import config_util
from .json_encoder import DateEncoder
from .models import UmKey, UmEventModel
from .um import um_tasks, um_util

CONTENT_TYPE_JSON = "application/json,charset=utf-8"


def get_event_md5(um_eventId: str, curr_date: str):
    """
    获取友盟自定义事件的md5值
        根据 事件id && 当前日期 生成md5值
    :param um_eventId:
    :param curr_date:
    :return:
    """
    md5_value: str = f"{um_eventId}{curr_date}"
    return hashlib.md5(md5_value.encode(encoding='utf-8')).hexdigest()


@require_http_methods(["POST"])
def um_event_op(request):
    """
    暂停友盟自定义事件
    op_type : 0=暂停，1=恢复
    :param request:
    :return:
    """
    post_body = json.loads(request.body)
    um_key: str = post_body.get('um_key')
    op_type: int = post_body.get('op_type') or 0
    ids: list = post_body.get('ids') or []

    config_util.parse_config(None)

    # 判断友盟key
    check_result_response = check_um_key(um_key=um_key)
    if check_result_response:
        return check_result_response

    # 判断友盟登录状态
    check_result_response = check_um_status(um_key=um_key)
    if check_result_response:
        return check_result_response

    # 批量暂停/恢复友盟统计事件
    _filter: Q = None
    for _id in ids:
        if not _filter:
            _filter = Q(um_eventId=_id)
        else:
            _filter = _filter | Q(um_eventId=_id)
    if op_type == 0:
        um_util.event_pause(um_key=um_key, ids=ids)
        UmEventModel.objects.filter(_filter).update(um_status='stopped')
    else:
        um_util.event_restore(um_key=um_key, ids=ids)
        UmEventModel.objects.filter(_filter).update(um_status='normal')
    r = {
        'code': 200,
        'msg': '操作成功',
        'data': None
    }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


@require_http_methods(["POST"])
def um_event(request):
    """
    查询所有友盟自定义事件
    :param request:
    :return:
    """
    post_body = json.loads(request.body)
    um_key: str = post_body.get('um_key')
    refresh: bool = post_body.get('refresh') == 1
    pg_index: str = post_body.get('pg_index') or 1
    pg_size: str = post_body.get('pg_size') or 20
    filter_dict: dict = post_body.get('filter') or None
    pg_start = (pg_index-1)*pg_size
    pg_end = pg_size*pg_index

    config_util.parse_config(None)

    # 判断友盟key
    check_result_response = check_um_key(um_key=um_key)
    if check_result_response:
        return check_result_response

    # 判断友盟登录状态
    if refresh:
        check_result_response = check_um_status(um_key=um_key)
        if check_result_response:
            return check_result_response

    curr_date: str = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    results: list = get_events_from_db(um_key=um_key, curr_date=curr_date, filter_dict=filter_dict)
    total: int = len(results)

    if refresh or len(results) == 0:
        results: list = list(um_tasks.get_analysis_event_list(um_key=um_key, refresh=refresh))
        total: int = len(results)

        # 将新结果插入数据库
        insert_event(results=results)

        # 重新查询数据库
        results: list = get_events_from_db(um_key=um_key, curr_date=curr_date, filter_dict=filter_dict)
    else:
        print('数据库已有数据，直接读取数据库的数据')

    r = {
        'code': 200,
        'msg': '查询成功',
        'data': {
            'lst': results[pg_start:pg_end],
            'total': total
        }
    }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


def insert_event(results: list):
    """
    将友盟自定义事件插入数据库
    :param results:
    :return:
    """
    print('将友盟自定义事件插入数据库')
    curr_date: str = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    for item in results or []:
        um_md5: str = get_event_md5(item.get('um_eventId'), curr_date)
        events = UmEventModel.objects.filter(um_md5=um_md5)
        force_update: bool = True if events and len(events) > 0 else False

        # 保存/更新入库
        if force_update:
            key = events[0]
        else:
            key = UmEventModel(um_md5=um_md5)

        key.um_key = item.get('um_key')
        key.um_eventId = item.get('um_eventId')
        key.um_name = item.get('um_name')
        key.um_displayName = item.get('um_displayName')
        key.um_status = item.get('um_status')
        key.um_eventType = item.get('um_eventType_int')
        key.um_countToday = item.get('um_countToday')
        key.um_countYesterday = item.get('um_countYesterday')
        key.um_deviceYesterday = item.get('um_deviceYesterday')
        key.um_date = curr_date
        key.save(force_update=force_update)
    print('入库完成')


def get_events_from_db(um_key: str, curr_date: str, filter_dict: dict):
    """
    从数据库中获取某一天的友盟自定义事件列表

    字段说明：https://www.cnblogs.com/ls1997/p/10955402.html
    _gt 大于>
    __gte 大于等于>=
    __lt 小于<
    __lte 小于等于<=
    __exact 精确等于 like 'aaa'
    __iexact 精确等于 忽略大小写 ilike 'aaa'
    __contains 包含 like '%aaa%'
    __icontains 包含,忽略大小写 ilike '%aaa%'，但是对于sqlite来说，contains的作用效果等同于icontains。
    __in Student.objects.filter(age__in=[10, 20, 30])
    __isnull 判空
    __startswith 以…开头
    __istartswith 以…开头 忽略大小写
    __endswith 以…结尾
    __iendswith 以…结尾，忽略大小写
    __range 在…范围内
    __year 日期字段的年份
    __month 日期字段的月份
    __day 日期字段的日
    :return:
    """
    order_by: str = None
    _filter: Q = Q(um_key=um_key) & Q(um_date=curr_date)
    if filter_dict:
        print(f"存在筛选条件，进行筛选查询：{filter_dict}")

        # 关键词
        keyword: str = filter_dict.get('keyword')
        if keyword:
            _filter = _filter & (Q(um_name__contains=keyword) | Q(um_displayName__contains=keyword))

        # 状态
        state: str = filter_dict.get('state')
        if state:
            _filter = _filter & Q(um_status=state)

        # 类型
        _type: str = filter_dict.get('type')
        if _type:
            _filter = _filter & Q(um_eventType=int(_type))

        # 排序方式
        order_by: str = filter_dict.get('order_by')
        if 'desc' == filter_dict.get('order'):
            order_by = f'-{order_by}'

    if order_by:
        obj = UmEventModel.objects.filter(_filter).order_by(order_by)
    else:
        obj = UmEventModel.objects.filter(_filter)

    return list(obj.values() or [])


@require_http_methods(["POST"])
def um_event_export(request):
    """
    导出所有友盟自定义事件
    :param request:
    :return:
    """
    post_body = json.loads(request.body)
    um_key: str = post_body.get('um_key')
    refresh: bool = post_body.get('refresh') == 1

    config_util.parse_config(None)

    # 判断友盟key
    check_result_response = check_um_key(um_key=um_key)
    if check_result_response:
        return check_result_response

    # 判断友盟登录状态
    check_result_response = check_um_status(um_key=um_key)
    if check_result_response:
        return check_result_response

    results: list = list(um_tasks.get_analysis_event_list(um_key=um_key, refresh=refresh))
    txt: str = None
    for item in results:
        if txt:
            txt = f"{txt}\n{item.get('um_name')},{item.get('um_displayName')},{item.get('um_eventType_int')}"
        else:
            txt = f"{item.get('um_name')},{item.get('um_displayName')},{item.get('um_eventType_int')}"
    r = {
        'code': 200,
        'msg': '查询成功',
        'data': txt
    }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


@require_http_methods(["POST"])
def um_event_import(request):
    """
    导入友盟事件
    :param request:
    :return:
    """
    um_key: str = ''.join(request.POST.values()) if request.POST else ""
    
    # 判断友盟key
    check_result_response = check_um_key(um_key=um_key)
    if check_result_response:
        return check_result_response

    # 判断友盟登录状态
    check_result_response = check_um_status(um_key=um_key)
    if check_result_response:
        return check_result_response

    code, msg = handle_uploaded_file(um_key=um_key, f=request.FILES['file'])
    r = {
        'code': code,
        'msg': msg,
        'data': None
    }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


@require_http_methods(["POST"])
def um_event_update(request):
    """
    导入&更新友盟友盟事件
    :param request:
    :return:
    """
    um_key: str = ''.join(request.POST.values()) if request.POST else ""
    code, msg = handle_update_file(um_key=um_key, f=request.FILES['file'])
    r = {
        'code': code,
        'msg': msg,
        'data': None
    }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


def handle_uploaded_file(um_key: str, f):
    """
    处理上传的文件
    :param um_key:
    :param f:
    :return:
    """

    if not um_key:
        return -1, "友盟key不能为空"

    # 保存文件
    file_path: str = f'{um_util.get_temp_file_dir()}/{f.name}'
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    if os.path.exists(file_path):
        print('文件保存成功，调用友盟的api进行批量上传自定义事件\n')
        code, msg = um_util.upload_event(um_key=um_key, file_path=file_path)

        print(f'\n删除刚才临时保存的文件：{file_path}')
        os.remove(file_path)
    else:
        print(f'文件上传失败，上传后的文件不存在：{file_path}')
        code, msg = -1, "上传失败，请稍候重试"

    return code, msg


def handle_update_file(um_key: str, f):
    """
    处理需要更新的友盟事件 上传的文件
    :param um_key:
    :param f:
    :return:
    """

    if not um_key:
        return -1, "友盟key不能为空"

    # 保存文件
    file_path: str = f'{um_util.get_temp_file_dir()}/um_keys_new_add.txt'
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    if os.path.exists(file_path):
        print('文件保存成功\n')
        code, msg = 200, "上传成功"
    else:
        print(f'文件上传失败，上传后的文件不存在：{file_path}')
        code, msg = -1, "上传失败，请稍候重试"

    return code, msg


def check_um_status(um_key: str) -> HttpResponse:
    """
    检查友盟连接状态，
    :param um_key:
    :return: None=状态正常，HttpResponse=状态异常，直接返回该response
    """
    status, msg = um_util.check_um_status(um_key=um_key)
    if status:
        return None
    else:
        r = {
            'code': 403,
            'msg': msg or '操作失败',
            'data': None
        }
        return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


def check_um_key(um_key: str) -> HttpResponse:
    """
    检查友盟key值，
    :param um_key:
    :return: None=状态正常，HttpResponse=状态异常，直接返回该response
    """
    if um_key:
        return None
    else:
        r = {
            'code': 200,
            'msg': '友盟key不能为空',
            'data': None
        }
        return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)
