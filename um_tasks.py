#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/26 上午11:19
# @Author  : Samge
import settings
import um_util


def do_um_synchro_task():
    """
    开始执行友盟同步任务
    :return:
    """
    check_env()
    um_util.cache_event_list(um_keys=[settings.UM_KEY_MASTER] + list(settings.UM_KEY_SLAVES))
    for um_key in settings.UM_KEY_SLAVES:
        um_util.update_um_data(um_key=um_key, um_key_source=settings.UM_KEY_MASTER)


def do_add_or_update_task():
    """
    执行添加/更新友盟自定义事件的任务
    :return:
    """
    check_env()
    um_util.cache_event_list(um_keys=[settings.UM_KEY_MASTER] + list(settings.UM_KEY_SLAVES))
    um_util.add_or_update_event_by_file(settings.UM_KEY_MASTER)


def check_env():
    """
    配置检测
    :return:
    """
    if not settings.X_XSRF_TOKEN:
        raise ValueError("请先在settings.py中配置 X_XSRF_TOKEN")
    if not settings.X_XSRF_TOKEN_HAITANG:
        raise ValueError("请先在settings.py中配置 X_XSRF_TOKEN_HAITANG")
    if not settings.COOKIE:
        raise ValueError("请先在settings.py中配置 COOKIE")
    if not settings.UM_KEY_MASTER:
        raise ValueError("请先在settings.py中配置 UM_KEY_MASTER")
    if not settings.UM_KEY_SLAVES:
        raise ValueError("请先在settings.py中配置 UM_KEY_SLAVES")
