#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/25 下午1:45
# @Author  : Samge
import settings
import um_util


def check_env():
    if not settings.X_XSRF_TOKEN:
        raise "请先在settings.py中配置 X_XSRF_TOKEN"
    if not settings.X_XSRF_TOKEN_HAITANG:
        raise "请先在settings.py中配置 X_XSRF_TOKEN_HAITANG"
    if not settings.COOKIE:
        raise "请先在settings.py中配置 COOKIE"
    if not settings.UM_KEY_MASTER:
        raise "请先在settings.py中配置 UM_KEY_MASTER"
    if not settings.UM_KEY_SLAVES:
        raise "请先在settings.py中配置 UM_KEY_SLAVES"


if __name__ == '__main__':
    check_env()
    um_util.cache_event_list(um_keys=[settings.UM_KEY_MASTER] + list(settings.UM_KEY_SLAVES))
    for um_key in settings.UM_KEY_SLAVES:
        um_util.update_um_data(um_key=um_key, um_key_source=settings.UM_KEY_MASTER)

