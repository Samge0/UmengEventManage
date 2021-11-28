#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/26 上午11:19
# @Author  : Samge
from ..um import um_util

# 配置
config = {}
# 主配置的友盟key
UM_KEY_MASTER = ''
# 其他需要更新的马甲的友盟key
UM_KEY_SLAVES = []


def do_um_synchro_task():
    """
    开始执行友盟同步任务
    :return:
    """
    # um_util.cache_event_list(um_keys=[UM_KEY_MASTER] + list(UM_KEY_SLAVES))
    for um_key in UM_KEY_SLAVES:
        um_util.update_um_data(um_key=um_key, um_key_source=UM_KEY_MASTER)


def do_add_or_update_task():
    """
    执行添加/更新友盟自定义事件的任务
    :return:
    """
    um_util.cache_event_list(um_keys=[UM_KEY_MASTER] + list(UM_KEY_SLAVES))
    um_util.add_or_update_event_by_file(UM_KEY_MASTER)



