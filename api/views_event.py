#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/3 下午4:29
# @Author  : Samge
import hashlib
import json
import os
import time

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from . import config_util
from .json_encoder import DateEncoder
from .models import UmKey, UmEventModel
from .um import um_tasks, um_util

CONTENT_TYPE_JSON = "application/json,charset=utf-8"


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
    results: list = get_events_from_db(um_key=um_key, curr_date=curr_date)
    total: int = len(results)

    if refresh or len(results) == 0:
        results: list = list(um_tasks.get_analysis_event_list(um_key=um_key, refresh=refresh))
        total: int = len(results)

        # 将新结果插入数据库
        insert_event(results=results)

        # 重新查询数据库
        results: list = get_events_from_db(um_key=um_key, curr_date=curr_date)
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


def get_events_from_db(um_key: str, curr_date: str):
    """
    从数据库中获取某一天的友盟自定义事件列表
    :return:
    """
    return list(UmEventModel.objects.filter(um_key=um_key, um_date=curr_date).values()) or []


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
