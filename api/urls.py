#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/26 上午10:27
# @Author  : Samge
from django.conf.urls import url
from .views import *
from .views_kv import *
from .views_event import *


# http路由
urlpatterns = [
    url(r'get_um_apps$', get_um_apps),
    url(r'get_um_keys$', get_um_keys),
    url(r'add_um_key$', add_um_key),
    url(r'del_um_key$', del_um_key),
    url(r'um_key_master$', um_key_master),

    url(r'get_kvs$', get_kvs),
    url(r'get_config$', get_config),
    url(r'save_config$', save_config),
    url(r'add_kv$', add_kv),
    url(r'add_kvs$', add_kvs),
    url(r'del_kv$', del_kv),
    url(r'kv_status$', kv_status),

    url(r'um_event$', um_event),
    url(r'um_event_export$', um_event_export),
    url(r'um_event_import$', um_event_import),
    url(r'um_event_update$', um_event_update),
    url(r'um_event_op$', um_event_op),
]
