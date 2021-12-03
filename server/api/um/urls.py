#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/25 下午1:55
# @Author  : Samge


BASE_URL = 'https://mobile.umeng.com/ht/api/v3/app/event'


# 自定义事件【获取今天&昨天统计的消息数量信息（只有状态正常的数据）】的api
API_EVENT_ANALYSIS_LIST = '{BASE_URL}/analysis/list?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【获取列表，状态status: normal、stopped、unregistered】的api
API_EVENT_LIST = '{BASE_URL}/list?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【批量还原】的api
API_EVENT_RESTORE = '{BASE_URL}/restore?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【批量暂停】的api
API_EVENT_PAUSE = '{BASE_URL}/pause?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【编辑】的api
API_EVENT_EDIT = '{BASE_URL}/edit?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【添加】的api
API_EVENT_ADD = '{BASE_URL}/add?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【批量复制】的api
API_EVENT_COPY = '{BASE_URL}/copy?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【批量导入文件】的api
API_EVENT_UPLOAD = '{BASE_URL}/upload?relatedId={um_key}&dataSourceId={um_key}'
# 自定义事件【获取限定数量额度】的api
API_EVENT_QUOTA = '{BASE_URL}/eventQuota?relatedId={um_key}&dataSourceId={um_key}'
