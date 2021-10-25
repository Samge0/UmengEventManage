#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/25 下午1:45
# @Author  : Samge


# 登录友盟后台，F12 获取的token跟cookie请求信息
CONTENT_TYPE = 'application/json;charset=UTF-8'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
X_XSRF_TOKEN = ''  # x-xsrf-token
X_XSRF_TOKEN_HAITANG = ''  #x-xsrf-token-haitang
COOKIE = ''


# 主配置的友盟key
UM_KEY_MASTER = ''
# 其他需要更新的马甲的友盟keys，字符数组
UM_KEY_SLAVES = []
