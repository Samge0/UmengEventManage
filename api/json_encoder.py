#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/19 下午2:38
# @Author  : Samge
import datetime
import json


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)
