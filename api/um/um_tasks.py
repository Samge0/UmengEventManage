#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/26 上午11:19
# @Author  : Samge
from .um_util import UmTask
from ..models import UserConfig


def do_um_synchro_task(u_id: str, um_socks) -> UmTask:
    """
    开始执行友盟同步任务
    :param u_id:
    :param um_socks:
    :return:
    """
    task: UmTask = UmTask(u_id=u_id, um_socks=um_socks)
    key_master, key_slaves = _get_um_key_config(u_id=u_id)
    if not key_master:
        return None
    task.cache_event_list(um_keys=[key_master] + list(key_slaves))
    for um_key in key_slaves:
        task.update_um_data(um_key=um_key, um_key_master=key_master)
    return task


def do_add_or_update_task(u_id: str, um_socks) -> UmTask:
    """
    执行添加/更新友盟自定义事件的任务
    :param u_id:
    :param um_socks:
    :return:
    """
    task: UmTask = UmTask(u_id=u_id, um_socks=um_socks)
    key_master, key_slaves = _get_um_key_config(u_id=u_id)
    if not key_master:
        return None
    # 根据友盟key获取对应的自定义事件列表最新数据并缓存到本地
    task.cache_event_list(um_keys=[key_master] + list(key_slaves))
    # 添加自定义事件，如果自定义事件已存在，则自动更新自定义事件显示名
    task.add_or_update_event_by_file(um_key=key_master)
    # 刷新本地数据库的友盟自定义事件
    task.refresh_local_db_events(um_key=key_master)
    return task


def get_all_event_list(u_id: str, um_key: str, refresh: bool):
    """
    获取友盟所有自定义事件列表（有效的&暂停的）
    :param u_id:
    :param um_key:
    :param refresh: 是否需要从网络中重新获取数据
    :return:
    """
    task: UmTask = UmTask(u_id=u_id, um_socks=None)

    need_refresh: bool = refresh \
                         or task.is_exists_pause(um_key=um_key) is False \
                         or task.is_exists_normal_analysis(um_key=um_key) is False
    if need_refresh:
        print(f'获取友盟自定义事件列表 需要刷新')
        task.cache_analysis_event_list(um_keys=[um_key])
    print(f'获取友盟自定义事件列表 直接从缓存中取')
    results: list = task.get_all_events_with_analysis(um_key=um_key)
    if need_refresh:
        task.insert_event(results=results)
    return results


def _get_um_key_config(u_id: str) -> (str, list):
    """
    获取友盟key配置信息
    :param u_id:
    :return:
    """
    values = UserConfig.objects.filter(u_id=u_id).values() or []
    if len(values) == 0:
        return '', []
    return values[0].get('uc_key_master'), values[0].get('uc_key_slaves').split('|')

