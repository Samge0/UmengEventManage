#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/26 上午10:27
# @Author  : Samge
from django.conf.urls import url
from .views.v_key import *


# http路由
urlpatterns = [
    url(r'^$', index, name='index'),
]
