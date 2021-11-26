#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/26 上午10:30
# @Author  : Samge
import json
import time

from channels.generic.websocket import WebsocketConsumer


# 消费者：友盟任务
class UmConsumer(WebsocketConsumer):

    def connect(self):
        print(f"UmConsumer connect 成功连接")
        self.accept()

    def disconnect(self, close_code):
        print(f"UmConsumer disconnect 断开连接 {close_code}")
        pass

    def receive(self, text_data):
        print(f"UmConsumer receive 接收数据：{text_data}")
        # text_data_json = json.loads(text_data)
        # message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': text_data
        }))

        for i in range(10):
            time.sleep(1)
            self.send(f"{i}")
        self.send(f"发送完毕")
