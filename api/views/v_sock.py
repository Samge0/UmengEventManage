#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/26 上午10:30
# @Author  : Samge
import json

from channels.generic.websocket import WebsocketConsumer

from api.um import um_tasks
from api.um.um_util import UmTask


class UmConsumer(WebsocketConsumer):
    """
    消费者：友盟任务
    """

    um_task: UmTask = None

    u_id: str = None

    def connect(self):
        self.u_id = self.scope['url_route']['kwargs']['u_id']
        print(f"UmConsumer connect 成功连接： {self.u_id}")
        self.accept()

    def disconnect(self, code):
        print(f"UmConsumer disconnect 断开连接 {code}")
        self.clear()

    def websocket_disconnect(self, code):
        print(f"UmConsumer websocket_disconnect 断开连接 {code}")
        self.clear()

    def close(self, code):
        print(f"UmConsumer close 断开连接 {code}")
        self.clear()

    def receive(self, text_data):
        print(f"UmConsumer receive 接收数据：{text_data}")
        self.parse_receive(text_data)

    def clear(self):
        if self.um_task:
            self.um_task.clear()

    def parse_receive(self, text_data):
        """
        处理接收到的消息
        :param text_data:
        :return:
        """
        msg_type: str = ''
        if '{' in text_data:
            text_data_json = json.loads(text_data) or {}
            msg_type = text_data_json.get('type')
        if 'syn' == msg_type:
            self.send(f"开始执行任务")
            self.um_task = um_tasks.do_um_synchro_task(u_id=self.u_id, um_socks=self)
            if self.um_task:
                self.send(f"任务完成")
            else:
                self.send(f"任务中止")

        elif 'update' == msg_type:
            self.send(f"开始执行任务")
            self.um_task = um_tasks.do_add_or_update_task(u_id=self.u_id, um_socks=self)
            if self.um_task:
                self.send(f"任务完成")
            else:
                self.send(f"任务中止")

        elif 'stop' == msg_type:
            self.send(f"断开上一个连接")
            self.clear()

        elif 'connect' == msg_type:
            self.send(f"已连接")

        else:
            self.send(f"消息口令不对: {msg_type}")
            self.send(f"任务中止")
