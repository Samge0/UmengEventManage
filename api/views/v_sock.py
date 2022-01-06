#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/26 上午10:30
# @Author  : Samge
import json

from channels.generic.websocket import WebsocketConsumer


from api.utils import u_config
from api.um import um_tasks, um_util


class UmConsumer(WebsocketConsumer):
    """
    消费者：友盟任务
    """

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
        msg_type: str = ''
        config: dict = None

        if '{' in text_data:
            text_data_json = json.loads(text_data) or {}
            msg_type = text_data_json.get('type')
            config = text_data_json.get('config')

        if is_bad_evn(self, config):
            return

        if 'syn' == msg_type:
            u_config.parse_config(config)
            if not is_bad_um_status(self, config):
                self.send(f"开始执行任务")
                um_util.um_socks = self
                um_tasks.do_um_synchro_task()
                self.send(f"任务完成")

        elif 'update' == msg_type:
            u_config.parse_config(config)
            if not is_bad_um_status(self, config):
                self.send(f"开始执行任务")
                um_util.um_socks = self
                um_tasks.do_add_or_update_task()
                self.send(f"任务执行完毕")

        elif 'stop' == msg_type:
            um_util.stop = True
            self.send(f"断开上一个连接")

        elif 'connect' == msg_type:
            self.send(f"已连接")

        else:
            self.send(f"消息口令不对: {msg_type}")
            self.send(f"任务已中止")


def is_bad_evn(self, config) -> str:
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
    if error_msg:
        self.send(f"任务执行中止")
    return error_msg


def is_bad_um_status(self, config) -> str:
    """
    配置友盟登录状态
    :return:
    """
    status, msg = um_util.check_um_status(um_key=config.get('UM_KEY_MASTER'))
    if status:
        return None
    self.send(msg)
    self.send(f"任务执行中止")
    return msg
