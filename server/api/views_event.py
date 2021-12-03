#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/3 下午4:29
# @Author  : Samge
import json
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from . import config_util
from .json_encoder import DateEncoder
from .models import UmKey
from .um import um_tasks

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
    if not um_key:
        r = {
            'code': 200,
            'msg': '查询失败，要查询的key为空',
            'data': list(UmKey.objects.filter().values())
        }
    else:
        config_util.parse_config(None)
        r = {
            'code': 200,
            'msg': '查询成功',
            'data': list(um_tasks.get_analysis_event_list(um_key=um_key, refresh=refresh))
        }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)
