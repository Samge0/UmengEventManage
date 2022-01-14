#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/5 上午10:37
# @Author  : Samge
import json
from django.http import HttpResponse
from api.utils.u_json import DateEncoder
from api.um import um_util

CONTENT_TYPE_JSON = "application/json,charset=utf-8"

# 用户id的字段名
UID = "HTTP_UMEM_UID"


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
            'code': 499,
            'msg': msg or '友盟连接状态异常，请尝试更新友盟cookie',
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


def get_r_dict(code: int, msg: str, data: object):
    """
    获取固定格式的响应体
    :param code:
    :param msg:
    :param data:
    :return:
    """
    return {
        'code': code,
        'msg': msg,
        'data': data
    }


def get_json_response(r):
    """
    获取json响应体
    :param r:
    :return:
    """
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


def get_uid(request) -> str:
    """
    获取当前请求中用户携带的uid信息，
        该信息由u_check.check_login装饰器统一处理
    :param request:
    :return: u_id
    """
    return request.META.get(UID) or ''
