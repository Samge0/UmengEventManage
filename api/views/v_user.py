#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/7 上午11:01
# @Author  : Samge
import json
import random
import time

from django.core import signing
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from api.models import User
from api.utils import u_http
from api.utils.u_json import DateEncoder


# 测试用的验证码，没做真实发送验证码动作
TEST_V_CODE = '666666'


def is_exist_user(u_id: str = '', u_email: str = '', u_phone: str = '', u_name: str = ''):
    """
    判断用户是否存在
    :param u_id:
    :param u_email:
    :param u_phone:
    :param u_name:
    :return:
    """
    if not u_id and not u_email and not u_phone and not u_name:
        return False
    _filter: Q = None
    if u_id:
        _filter = Q(u_id=u_id)
    if u_email:
        _filter = _filter | Q(u_email=u_email) if _filter else Q(u_email=u_email)
    if u_phone:
        _filter = _filter | Q(u_phone=u_phone) if _filter else Q(u_phone=u_phone)
    if u_name:
        _filter = _filter | Q(u_name=u_name) if _filter else Q(u_name=u_name)
    return len(User.objects.filter(_filter) or []) > 0


def get_user(u_name: str, u_pw: str):
    """
    根据账号密码获取用户信息
    :param u_name:
    :param u_pw:
    :return:
    """
    _filter: Q = (Q(u_name=u_name) | Q(u_email=u_name) | Q(u_phone=u_name)) & Q(u_pw=u_pw)
    users = User.objects.filter(_filter)
    if len(users or []) > 0:
        return users[0]
    else:
        return None


def get_random_uid() -> str:
    """
    获取7位随机uid
        暂且使用7位的uid
    :return:
    """
    u_id: str = "".join(random.choice("0123456789") for i in range(7))
    if is_exist_user(u_id=u_id):
        return get_random_uid()
    else:
        return u_id


def create_token(u_id: str) -> str:
    """
    生成token
    :param u_id:
    :return:
    """
    v: dict = {
        't': time.time(),
        'u_id': u_id
    }
    return signing.dumps(v)


@require_http_methods(["POST"])
def reg(request):
    post_body = json.loads(request.body)
    u_phone = post_body.get('u_phone') or ""
    u_email = post_body.get('u_email') or ""
    u_code = post_body.get('u_code') or ""
    u_name = post_body.get('u_name') or u_phone or u_email
    u_pw = post_body.get('u_pw') or ""

    if not u_email and not u_phone:
        code, msg, data = 400, '账号不能为空', None
    elif not u_code or not u_pw:
        code, msg, data = 400, '验证码、密码不能为空', None
    elif len(u_pw) < 6:
        code, msg, data = 400, '密码最小长度需要6个字符', None
    elif u_code != TEST_V_CODE:
        code, msg, data = 400, '验证码错误', None
    else:
        if is_exist_user(u_phone=u_phone):
            code, msg, data = 400, '该手机号已被注册', None
        elif is_exist_user(u_email=u_email):
            code, msg, data = 400, '该邮箱已被注册', None
        elif is_exist_user(u_name=u_name):
            code, msg, data = 400, '该用户名已被注册', None
        else:
            u_id: str = get_random_uid()
            u_token: str = create_token(u_id=u_id)
            User(u_id=u_id, u_name=u_name, u_pw=u_pw, u_phone=u_phone, u_email=u_email, u_token=u_token).save()
            data: dict = {
                'u_id': u_id,
                'u_name': u_name,
                'u_email': u_email,
                'u_token': u_token,
            }
            code, msg, data = 200, '注册成功', data
    r = {
        'code': code,
        'msg': msg,
        'data': data
    }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=u_http.CONTENT_TYPE_JSON)


@require_http_methods(["POST"])
def login(request):
    post_body = json.loads(request.body)
    u_name = post_body.get('u_name') or ''
    u_pw = post_body.get('u_pw') or ""

    if not u_name or not u_pw:
        code, msg, data = 400, '用户名、密码不能为空', None
    else:
        user: User = get_user(u_name=u_name, u_pw=u_pw)
        if not user:
            code, msg, data = 400, '登录失败', None
        else:
            # 更新token & 最后登录时间
            u_id: str = user.u_id
            u_token: str = create_token(u_id=u_id)
            user.u_token = u_token
            user.u_last_time = timezone.now()
            user.save(force_update=True)

            data: dict = {
                'u_id': user.u_id,
                'u_name': user.u_name,
                'u_email': user.u_email,
                'u_phone': user.u_phone,
                'u_token': u_token,
            }
            code, msg, data = 200, '登录成功', data

    r = {
        'code': code,
        'msg': msg,
        'data': data
    }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=u_http.CONTENT_TYPE_JSON)
