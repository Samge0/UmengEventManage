#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/14 下午2:31
# @Author  : Samge
import hashlib


def get_kv_md5(u_id: str, kv_key: str):
    """
    获取 键值对管理 的md5值
    :param u_id:
    :param kv_key:
    :return:
    """
    md5_value: str = f"{u_id}_{kv_key}"
    return get_md5(md5_value)


def get_um_key_md5(u_id: str, um_key: str):
    """
    获取 友盟key 的md5值
    :param u_id:
    :param um_key:
    :return:
    """
    md5_value: str = f"{u_id}_{um_key}"
    return get_md5(md5_value)


def get_event_md5(u_id: str, um_eventId: str, curr_date: str):
    """
    获取友盟自定义事件的md5值
    :param u_id:
    :param um_eventId:
    :param curr_date:
    :return:
    """
    md5_value: str = f"{u_id}_{um_eventId}_{curr_date}"
    return get_md5(md5_value)


def get_md5(md5_value: str):
    """
    将字符串转md5
    :param md5_value:
    :return:
    """
    return hashlib.md5(md5_value.encode(encoding='utf-8')).hexdigest()
