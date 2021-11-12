#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/25 下午1:45
# @Author  : Samge
import settings
import um_util


def do_um_synchro_task():
    """
    开始执行友盟同步任务
    :return:
    """
    um_util.check_env()
    um_util.cache_event_list(um_keys=[settings.UM_KEY_MASTER] + list(settings.UM_KEY_SLAVES))
    for um_key in settings.UM_KEY_SLAVES:
        um_util.update_um_data(um_key=um_key, um_key_source=settings.UM_KEY_MASTER)


def do_add_or_update_task():
    """
    执行添加/更新友盟自定义事件的任务
    :return:
    """
    um_util.check_env()
    um_util.cache_event_list(um_keys=[settings.UM_KEY_MASTER] + list(settings.UM_KEY_SLAVES))
    um_util.add_or_update_event_by_file(settings.UM_KEY_MASTER)


if __name__ == '__main__':
    do_um_synchro_task()
    # do_add_or_update_task()

