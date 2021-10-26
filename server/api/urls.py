#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/26 上午10:27
# @Author  : Samge
from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'get_um_keys$', get_um_keys),
    url(r'add_um_key$', add_um_key),
    url(r'del_um_key$', del_um_key),
    url(r'um_key_master$', um_key_master),
]
