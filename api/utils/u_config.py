#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/3 下午4:44
# @Author  : Samge
from api.models import KeyValue
from api.um import um_tasks, um_util
from api.utils import u_md5


def get_key_value(u_id: str, config: dict, kv_key: str):
    """
    根据key名读取数据库的值
    :param u_id:
    :param config:
    :param kv_key:
    :return:
    """
    kv_md5: str = u_md5.get_kv_md5(u_id=u_id, kv_key=kv_key)
    keys = KeyValue.objects.filter(kv_md5=kv_md5)
    if keys:
        config[kv_key] = keys[0].kv_value


def get_config(u_id: str):
    """
    从数据库中读取配置
    :return:
    """
    config: dict = {}
    get_key_value(u_id, config, "CONTENT_TYPE")
    get_key_value(u_id, config, "USER_AGENT")
    get_key_value(u_id, config, "X_XSRF_TOKEN")
    get_key_value(u_id, config, "X_XSRF_HAITANG")
    get_key_value(u_id, config, "COOKIE")
    get_key_value(u_id, config, "UM_KEY_MASTER")
    get_key_value(u_id, config, "UM_KEY_SLAVES")
    return config


def parse_config(u_id: str, config: dict):
    """
    处理配置，并将配置信息复制给工具类
    :param u_id: 客户端传过来的配置信息，如果传空，则服务端从数据库中读取默认的配置信息
    :param config: 客户端传过来的配置信息，如果传空，则服务端从数据库中读取默认的配置信息
    :return:
    """
    if not config:
        config = get_config(u_id=u_id)
    um_tasks.UM_KEY_MASTER = config.get('UM_KEY_MASTER') or ''
    um_tasks.UM_KEY_SLAVES = (config.get('UM_KEY_SLAVES') or '').split('|') or []
    um_util.default_headers = get_header(config)


def get_header(config):
    """
    获取友盟操作的请求头
    :param config:
    :return:
    """
    return {
        'user-agent': config.get('USER_AGENT'),
        'x-xsrf-token': config.get('X_XSRF_TOKEN'),
        'x-xsrf-token-haitang': config.get('X_XSRF_HAITANG'),
        'content-type': config.get('CONTENT_TYPE'),
        'cookie': config.get('COOKIE'),
    }
