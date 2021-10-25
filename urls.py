#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/25 下午1:55
# @Author  : Samge


# 自定义事件【获取列表（生效的）】的api
API_EVENT_LIST = 'https://mobile.umeng.com/ht/api/v3/app/event/list?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【获取列表（暂停的）】的api
API_EVENT_PAUSE_LIST = 'https://mobile.umeng.com/ht/api/v3/app/event/list?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【批量还原】的api
API_EVENT_RESTORE = 'https://mobile.umeng.com/ht/api/v3/app/event/restore?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【批量暂停】的api
API_EVENT_PAUSE = 'https://mobile.umeng.com/ht/api/v3/app/event/pause?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【编辑】的api
API_EVENT_EDIT = 'https://mobile.umeng.com/ht/api/v3/app/event/edit?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【批量复制】的api
API_EVENT_COPY = 'https://mobile.umeng.com/ht/api/v3/app/event/copy?relatedId={um_key}&dataSourceId={um_key}'
