#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/3 下午4:29
# @Author  : Samge
import json
import os

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from . import config_util
from .json_encoder import DateEncoder
from .models import UmKey
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
    if not um_key:
        r = {
            'code': 200,
            'msg': '查询失败，要查询的key为空',
            'data': list(UmKey.objects.filter().values())
        }
    else:
        config_util.parse_config(None)
        results: list = list(um_tasks.get_analysis_event_list(um_key=um_key, refresh=refresh))
        total: int = len(results)
        r = {
            'code': 200,
            'msg': '查询成功',
            'data': {
                'lst': results[pg_start:pg_end],
                'total': total
            }
        }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


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
    if not um_key:
        r = {
            'code': 200,
            'msg': '导出失败，要查询的key为空',
            'data': list(UmKey.objects.filter().values())
        }
    else:
        config_util.parse_config(None)
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
    code, msg = handle_uploaded_file(um_key=um_key, f=request.FILES['file'])
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
