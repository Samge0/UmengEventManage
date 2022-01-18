#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/7 上午10:07
# @Author  : Samge

import time

from django.core import signing
from django.db.models import Q

from api.models import User
from api.utils import u_http

# token过期时间，单位：秒
TOKEN_EXPIRE_TIME = 60 * 60 * 24 * 365


def check_login(func):
    """
    验证是否登录的装饰器
    :param func:
    :return:
    """
    def inner(*args, **kwargs):
        token = args[0].META.get("HTTP_AUTHORIZATION")
        code, msg, user_dict = check_token_status(token)
        if code != 200:
            r = {
                'code': code,
                'msg': msg,
                'data': None
            }
            return u_http.get_json_response(r)
        # 校验成功，将用户id放入请求对象体中
        args[0].META[u_http.UID] = user_dict.get('u_id')
        return func(*args, **kwargs)
    return inner


def check_token_status(token: str) -> (int, str):
    """
    检查token状态
    :param token:
    :return:
    """
    try:
        user_dict: dict = signing.loads(token)
    except:
        return 401, '请重新登录', None

    # 检查token是否变化：修改密码或者重新登录后都会变化
    u_id: str = user_dict.get('u_id')
    _filter: Q = Q(u_id=u_id) & Q(u_token=token)
    users = User.objects.filter(_filter)
    if len(users or []) == 0:
        return 403, '登录信息已过期，请重新登录', None

    # 检查是否过期
    t = user_dict.get('t')
    if time.time() - t > TOKEN_EXPIRE_TIME:
        user = users[0]
        user.u_token = ''
        user.save(force_update=True)
        return 403, '登录信息已过期，请重新登录', None

    return 200, '验证通过', user_dict
