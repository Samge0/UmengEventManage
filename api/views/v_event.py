#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/3 下午4:29
# @Author  : Samge
import json
import os
import time

from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from api.models import UmEventModel
from api.um import um_tasks
from api.um.um_util import UmTask
from api.utils import u_http, u_md5
from api.utils.u_check import check_login
from api.utils.u_json import DateEncoder


@check_login
@require_http_methods(["POST"])
def um_event_op(request):
    """
    暂停/恢复 友盟自定义事件
    op_type : 0=暂停，1=恢复
    :param request:
    :return:
    """
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    um_key: str = post_body.get('um_key')
    op_type: int = post_body.get('op_type') or 0
    ids: list = post_body.get('ids') or []

    # 判断友盟key
    check_result_response = check_um_key(um_key=um_key)
    if check_result_response:
        return check_result_response

    # 判断友盟登录状态
    check_result_response = check_um_status(u_id=u_id, um_key=um_key)
    if check_result_response:
        return check_result_response

    # 批量暂停/恢复友盟统计事件
    _filter: Q = None
    for _id in ids:
        if not _filter:
            _filter = Q(um_eventId=_id)
        else:
            _filter = _filter | Q(um_eventId=_id)

    task: UmTask = UmTask(u_id=u_id, um_socks=None)
    if op_type == 0:
        task.event_pause(um_key=um_key, ids=ids)
        UmEventModel.objects.filter(_filter).update(um_status='stopped')
    else:
        task.event_restore(um_key=um_key, ids=ids)
        UmEventModel.objects.filter(_filter).update(um_status='normal')
    r = u_http.get_r_dict(
        code=200,
        msg='操作成功',
        data=None
    )
    return u_http.get_json_response(r)


@check_login
@require_http_methods(["POST"])
def um_event(request):
    """
    查询所有友盟自定义事件
    :param request:
    :return:
    """
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    um_key: str = post_body.get('um_key')
    refresh: bool = post_body.get('refresh') == 1
    pg_index: str = post_body.get('pg_index') or 1
    pg_size: str = post_body.get('pg_size') or 20
    filter_dict: dict = post_body.get('filter') or {}
    pg_start = (pg_index-1)*pg_size
    pg_end = pg_size*pg_index

    # 判断友盟key
    check_result_response = check_um_key(um_key=um_key)
    if check_result_response:
        return check_result_response

    # 判断友盟登录状态
    if refresh:
        check_result_response = check_um_status(u_id=u_id, um_key=um_key)
        if check_result_response:
            return check_result_response

    curr_date: str = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    results: list = get_events_from_db(u_id=u_id, um_key=um_key, curr_date=curr_date, filter_dict=filter_dict)
    need_refresh = refresh or (len(results) == 0 and len(filter_dict or {}) == 0)

    if need_refresh:
        results: list = list(um_tasks.get_analysis_event_list(u_id=u_id, um_key=um_key, refresh=refresh))
        # 将新结果插入数据库
        insert_event(u_id=u_id, results=results)
        # 重新查询数据库
        results: list = get_events_from_db(u_id=u_id, um_key=um_key, curr_date=curr_date, filter_dict=filter_dict)
    else:
        print('数据库已有数据，直接读取数据库的数据')

    r = u_http.get_r_dict(
        code=200,
        msg='查询成功',
        data={
            'lst': results[pg_start:pg_end],
            'total': len(results)
        }
    )
    return u_http.get_json_response(r)


def insert_event(u_id: str, results: list):
    """
    将友盟自定义事件插入数据库
    :param u_id:
    :param results:
    :return:
    """
    print('将友盟自定义事件插入数据库')
    curr_date: str = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    for item in results or []:
        um_md5: str = u_md5.get_event_md5(u_id, item.get('um_eventId'), curr_date)
        events = UmEventModel.objects.filter(um_md5=um_md5)
        force_update: bool = True if events and len(events) > 0 else False

        # 保存/更新入库
        if force_update:
            key = events[0]
        else:
            key = UmEventModel(um_md5=um_md5)

        key.u_id = u_id
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


def get_events_from_db(u_id: str, um_key: str, curr_date: str, filter_dict: dict):
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

    不等于/不包含于：
        XXX.objects.filter().excute(age=10) // 查询年龄不为10的学生
        XXX.objects.filter().excute(age__in=[10, 20]) // 查询年龄不在 [10, 20] 的学生
    :return:
    """
    order_by: str = None
    _filter: Q = Q(u_id=u_id) & Q(um_key=um_key) & Q(um_date=curr_date)
    if filter_dict and len(filter_dict or {}) > 0:
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

        # 数量限制
        count_limit: dict = filter_dict.get('count_limit') or None
        if count_limit:
            # 处理昨日消息数筛选
            yesterday_min, yesterday_max = get_min_max(count_limit, 'yesterday_min', 'yesterday_max')
            if yesterday_min == 0 and yesterday_max == 0:
                _filter = _filter & Q(um_countYesterday=0)
            elif yesterday_max > 0:
                _filter = _filter & Q(um_countYesterday__gte=yesterday_min) & Q(um_countYesterday__lte=yesterday_max)

            # 处理今日消息数筛选
            today_min, today_max = get_min_max(count_limit, 'today_min', 'today_max')
            if today_min == 0 and today_max == 0:
                _filter = _filter & Q(um_countToday=0)
            elif today_max > 0:
                _filter = _filter & Q(um_countToday__gte=today_min) & Q(um_countToday__lte=today_max)

            # 处理设备消息数筛选
            device_min, device_max = get_min_max(count_limit, 'device_min', 'device_max')
            if device_min == 0 and device_max == 0:
                _filter = _filter & Q(um_deviceYesterday=0)
            elif device_max > 0:
                _filter = _filter & Q(um_deviceYesterday__gte=device_min) & Q(um_deviceYesterday__lte=device_max)

        # 排序方式
        order_by: str = filter_dict.get('order_by')
        if 'desc' == filter_dict.get('order'):
            order_by = f'-{order_by}'
    else:
        # 状态，如果筛选条件不传, 默认查状态正常的数据
        _filter = _filter & Q(um_status='normal')

    if order_by:
        obj = UmEventModel.objects.filter(_filter).order_by(order_by)
    else:
        obj = UmEventModel.objects.filter(_filter)

    return list(obj.values() or [])


def get_min_max(count_limit, key_min, key_max):
    """
    获取最大最小值
    :param count_limit:
    :param key_min:
    :param key_max:
    :return:
    """
    _max: int = count_limit.get(key_max) if count_limit.get(key_max) is not None else -1
    _min: int = count_limit.get(key_min) if count_limit.get(key_min) is not None else -1
    _min: int = _max if _min > _max else _min
    return _min, _max


@check_login
@require_http_methods(["POST"])
def um_event_export(request):
    """
    导出所有友盟自定义事件
    :param request:
    :return:
    """
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    um_key: str = post_body.get('um_key')
    refresh: bool = post_body.get('refresh') == 1

    # 判断友盟key
    check_result_response = check_um_key(um_key=um_key)
    if check_result_response:
        return check_result_response

    # 判断友盟登录状态
    check_result_response = check_um_status(u_id=u_id, um_key=um_key)
    if check_result_response:
        return check_result_response

    results: list = list(um_tasks.get_analysis_event_list(u_id=u_id, um_key=um_key, refresh=refresh))
    txt: str = None
    for item in results:
        if txt:
            txt = f"{txt}\n{item.get('um_name')},{item.get('um_displayName')},{item.get('um_eventType_int')}"
        else:
            txt = f"{item.get('um_name')},{item.get('um_displayName')},{item.get('um_eventType_int')}"
    r = u_http.get_r_dict(
        code=200,
        msg='查询成功',
        data=txt
    )
    return u_http.get_json_response(r)


@check_login
@require_http_methods(["POST"])
def um_event_import(request):
    """
    导入友盟事件
    :param request:
    :return:
    """
    u_id: str = u_http.get_uid(request)

    um_key: str = ''.join(request.POST.values()) if request.POST else ""

    # 判断友盟key
    check_result_response = check_um_key(um_key=um_key)
    if check_result_response:
        return check_result_response

    # 判断友盟登录状态
    check_result_response = check_um_status(u_id=u_id, um_key=um_key)
    if check_result_response:
        return check_result_response

    code, msg = handle_uploaded_file(u_id=u_id, um_key=um_key, f=request.FILES['file'])
    r = u_http.get_r_dict(
        code=code,
        msg=msg,
        data=None
    )
    return u_http.get_json_response(r)


@check_login
@require_http_methods(["POST"])
def um_event_update(request):
    """
    导入&更新友盟友盟事件
    :param request:
    :return:
    """
    u_id: str = u_http.get_uid(request)

    um_key: str = ''.join(request.POST.values()) if request.POST else ""
    code, msg = handle_update_file(u_id=u_id, um_key=um_key, f=request.FILES['file'])
    r = u_http.get_r_dict(
        code=code,
        msg=msg,
        data=None
    )
    return u_http.get_json_response(r)


def handle_uploaded_file(u_id: str, um_key: str, f):
    """
    处理上传的文件
    :param u_id:
    :param um_key:
    :param f:
    :return:
    """

    if not um_key:
        return -1, "友盟key不能为空"

    # 保存文件
    task: UmTask = UmTask(u_id=u_id, um_socks=None)
    file_path: str = f'{task.get_temp_file_dir()}/{f.name}'
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    if os.path.exists(file_path):
        print('文件保存成功，调用友盟的api进行批量上传自定义事件\n')
        code, msg = task.upload_event(um_key=um_key, file_path=file_path)

        print(f'\n删除刚才临时保存的文件：{file_path}')
        os.remove(file_path)
    else:
        print(f'文件上传失败，上传后的文件不存在：{file_path}')
        code, msg = -1, "上传失败，请稍候重试"

    return code, msg


def handle_update_file(u_id: str, um_key: str, f):
    """
    处理需要更新的友盟事件 上传的文件
    :param u_id:
    :param um_key:
    :param f:
    :return:
    """

    if not um_key:
        return -1, "友盟key不能为空"

    # 保存文件
    task: UmTask = UmTask(u_id=u_id, um_socks=None)
    file_path: str = f'{task.get_temp_file_dir()}/um_keys_new_add.txt'
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


def check_um_status(u_id: str, um_key: str) -> HttpResponse:
    """
    检查友盟连接状态，
    :param u_id:
    :param um_key:
    :return: None=状态正常，HttpResponse=状态异常，直接返回该response
    """
    task: UmTask = UmTask(u_id=u_id, um_socks=None)
    status, msg = task.check_um_status(um_key=um_key)
    if status:
        return None
    else:
        r = {
            'code': 499,
            'msg': msg or '友盟连接状态异常，请尝试更新友盟cookie',
            'data': None
        }
        return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=u_http.CONTENT_TYPE_JSON)


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
        return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=u_http.CONTENT_TYPE_JSON)
