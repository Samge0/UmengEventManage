#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/5 上午10:37
# @Author  : Samge
import json

from django.http import HttpResponse

from api.utils.u_json import DateEncoder

CONTENT_TYPE_JSON = "application/json,charset=utf-8"

# 用户id的字段名
UID = "HTTP_UMEM_UID"


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
