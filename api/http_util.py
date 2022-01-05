#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/5 上午10:37
# @Author  : Samge
import json
from django.http import HttpResponse
from api.json_encoder import DateEncoder
from api.um import um_util

CONTENT_TYPE_JSON = "application/json,charset=utf-8"


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
        return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=http_util.CONTENT_TYPE_JSON)


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
        return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=http_util.CONTENT_TYPE_JSON)