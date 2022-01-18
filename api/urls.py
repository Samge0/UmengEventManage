#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/26 上午10:27
# @Author  : Samge
from django.conf.urls import url

from .views.v_config import *
from .views.v_event import *
from .views.v_key import *
from .views.v_user import *

# http路由
urlpatterns = [
    url(r'get_um_keys$', get_um_keys),
    url(r'add_um_key$', add_um_key),
    url(r'del_um_key$', del_um_key),
    url(r'um_key_master$', um_key_master),

    url(r'get_config$', get_config),
    url(r'save_config$', save_config),

    url(r'um_event$', um_event),
    url(r'um_event_export$', um_event_export),
    url(r'um_event_import$', um_event_import),
    url(r'um_event_update$', um_event_update),
    url(r'um_event_op$', um_event_op),

    url(r'reg$', reg),
    url(r'login$', login),
]
