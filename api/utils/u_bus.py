#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/14 下午5:05
# @Author  : Samge


def has_key(_dict: dict, _key: str) -> bool:
    """
    判断字典是否存在key
    :param _dict:
    :param _key:
    :return:
    """
    return _dict and _key in _dict.keys()


class PyBus (object):

    subs: dict = {}

    def __init__(self,):
        self.clear()

    def clear(self):
        """
        清除订阅
        :return:
        """
        self.subs: dict = {}

    def subscribe(self, owner: str, subject: str, func):
        """
        订阅
        :param owner:       订阅归属（一级目录key）
        :param subject:     订阅主题/订阅key（二级目录key）
        :param func:        回调方法
        :return:
        """
        if not has_key(_dict=self.subs, _key=owner):
            self.subs[owner] = {}
        self.subs[owner][subject] = func

    def has_subs(self, owner: str, subject: str):
        """
        是否存在订阅
        :param owner:       订阅归属（一级目录key）
        :param subject:     订阅主题/订阅key（二级目录key）
        :return:
        """
        return has_key(_dict=self.subs, _key=owner) \
               and has_key(_dict=self.subs[owner], _key=subject)

    def publish(self, subject: str, *args, **kwargs):
        """
        发布
        :param subject:     订阅主题/订阅key（二级目录key）
        :param args:        参数组
        :param kwargs:      字典数据
        :return:
        """
        for key, value in self.subs.items():
            if has_key(_dict=value, _key=subject):
                value[subject](*args, **kwargs)
