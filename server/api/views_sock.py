#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/26 上午10:30
# @Author  : Samge
import json
import time

from channels.generic.websocket import WebsocketConsumer


# 消费者：友盟任务
from .um import um_tasks, um_util


class UmConsumer(WebsocketConsumer):

    def connect(self):
        print(f"UmConsumer connect 成功连接")
        self.accept()
        um_util.stop = False

    def disconnect(self, code):
        print(f"UmConsumer disconnect 断开连接 {code}")

    def websocket_disconnect(self, code):
        print(f"UmConsumer websocket_disconnect 断开连接 {code}")

    def close(self, code):
        print(f"UmConsumer close 断开连接 {code}")

    def receive(self, text_data):
        print(f"UmConsumer receive 接收数据：{text_data}")
        type = -1
        config = None

        if '{' in text_data:
            text_data_json = json.loads(text_data) or {}
            type = text_data_json.get('type')
            config = text_data_json.get('config')

        # message = text_data_json['message']

        # self.send(msg=json.dumps({
        #     'message': msg
        # }))

        # for i in range(10):
        #     time.sleep(1)
        #     self.send(f"{i}")

        error_msg: str = check_env(self, config)
        if error_msg:
            self.send(f"任务执行完毕")
            return

        if 'syn' == type:
            self.send(f"开始执行任务")
            um_util.um_socks = self
            parse_config(config)
            um_tasks.do_um_synchro_task()
            self.send(f"任务完成")

        elif 'update' == type:
            self.send(f"开始执行任务")
            um_util.um_socks = self
            parse_config(config)
            um_tasks.do_add_or_update_task()
            self.send(f"任务执行完毕")

        elif 'stop' == type:
            um_util.stop = True
            self.send(f"任务已中止")

        else:
            print("消息口令不对")
            self.send("已连接")


def parse_config(config):
    if config:
        um_tasks.UM_KEY_MASTER = config.get('UM_KEY_MASTER') or ''
        um_tasks.UM_KEY_SLAVES = config.get('UM_KEY_SLAVES') or []
        um_util.default_headers = get_header(config)


def get_header(config):
    return {
        'user-agent': config.get('USER_AGENT'),
        'x-xsrf-token': config.get('X_XSRF_TOKEN'),
        'x-xsrf-token-haitang': config.get('X_XSRF_HAITANG'),
        'content-type': config.get('CONTENT_TYPE'),
        'cookie': config.get('COOKIE'),
    }


def check_env(self, config):
    """
    配置检测
    :return:
    """
    if not config:
        error_msg = "配置不能为空"
        self.send(error_msg)
        return error_msg
    error_msg: str = None
    if not config.get('X_XSRF_TOKEN'):
        error_msg = "请先配置 X_XSRF_TOKEN"
        self.send(error_msg)
    if not config.get('X_XSRF_HAITANG'):
        error_msg = "请先配置 X_XSRF_HAITANG"
        self.send(error_msg)
    if not config.get('COOKIE'):
        error_msg = "请先配置 COOKIE"
        self.send(error_msg)
    if not config.get('UM_KEY_MASTER'):
        error_msg = "请先配置 UM_KEY_MASTER"
        self.send(error_msg)
    if not config.get('UM_KEY_SLAVES'):
        error_msg = "请先配置 UM_KEY_SLAVES"
        self.send(error_msg)
    return error_msg
