#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/25 下午1:45
# @Author  : Samge
import json
import random
import re
import time
import requests as requests
import file_util
import settings
import urls

true = True
false = False
null = None


def update_um_data(um_key: str, um_key_source: str):
    """
    更新友盟 自定义事件 数据
    :param um_key: 要更新的友盟key
    :param um_key_source: 源友盟key
    :return:
    """
    print(f'正在更新：{um_key}')

    print(f'\n1、暂停所有自定义事件：{um_key}')
    event_pause_all(um_key=um_key)

    print(f'\n2、复制自定义事件： {um_key_source} 复制到==》{um_key}')
    copy_event(um_key=um_key, um_key_source=um_key_source)

    print(f'\n3、再次暂停所有自定义事件：{um_key}')
    event_pause_all(um_key=um_key)

    print(f'\n4、重新拉取自定义事件状态列表：{um_key}')
    cache_event_list(um_keys=[um_key])

    print(f'\n5、批量恢复自定义事件，根据指定源进行恢复： {um_key_source} 恢复到==》{um_key}')
    event_restore_bysource(um_key=um_key, um_key_source=um_key_source)

    print(f'\n6、重新拉取自定义事件状态列表：{um_key}')
    cache_event_list(um_keys=[um_key])

    print(f'\n7、更新自定义事件-》计算事件（calculation）：{um_key}')
    update_event_multiattribute_to_calculation(um_key=um_key)

    print(f'\n8、同步更新自定义事件的显示名称：{um_key_source} 同步到==》{um_key}')
    update_event_display_name(um_key=um_key, um_key_source=um_key_source)

    print(f'所有操作已完成：{um_key}\n 点击 https://mobile.umeng.com/platform/{um_key}/setting/event/list 查看')


def get_default_headers():
    """
    获取默认的请求头
    :return:
    """
    return {
        'user-agent': settings.USER_AGENT,
        'x-xsrf-token': settings.X_XSRF_TOKEN,
        'x-xsrf-token-haitang': settings.X_XSRF_TOKEN_HAITANG,
        'content-type': settings.CONTENT_TYPE,
        'cookie': settings.COOKIE,
    }


def get_post_json(data: dict):
    return json.dumps(data, ensure_ascii=False).encode('utf-8')


def get_event_list(um_key: str):
    """
    获取自定义事件列表（有效的）
    :param um_key: 友盟key，每隔应用单独的key
    :return:
    """
    url: str = urls.API_EVENT_LIST.format(um_key=um_key)
    data: dict = {
        "relatedId": um_key,
        "sortBy": "countToday",
        "sortType": "desc",
        "version": "",
        "page": 1,
        "pageSize": 500,
        "dataSourceId": um_key
    }
    r = requests.post(url=url, headers=get_default_headers(), data=get_post_json(data))
    if is_response_ok(r):
        print(f'获取自定义事件列表（有效的）成功：{um_key}')
        file_util.save_txt_file(r.text, f'temp_files/event_lst_{um_key}.txt')
    else:
        print(f'获取自定义事件列表（有效的）失败：{get_fail_msg(um_key=um_key, r=r)}')


def get_event_pause_list(um_key: str):
    """
    获取自定义事件列表（暂停的）
    :param um_key: 友盟key，每隔应用单独的key
    :return:
    """
    url: str = urls.API_EVENT_PAUSE_LIST.format(um_key=um_key)
    data: dict = {
        "appkey": um_key,
        "status": "stopped",
        "page": 1,
        "pageSize": 2000,
        "relatedId": um_key,
        "dataSourceId": um_key
    }
    r = requests.post(url=url, headers=get_default_headers(), data=get_post_json(data))
    if is_response_ok(r):
        print(f'获取自定义事件列表（暂停的）成功：{um_key}')
        file_util.save_txt_file(r.text, f'temp_files/event_lst_{um_key}_pause.txt')
    else:
        print(f'获取自定义事件列表（暂停的）失败：{get_fail_msg(um_key=um_key, r=r)}')


def edit_event(um_key: str, event_id: str, display_name: str):
    """
    修改 自定义事件
    :param um_key: 友盟key，每隔应用单独的key
    :param event_id: 自定义事件id
    :param display_name: 自定义事件显示的名称
    :return:
    """
    url: str = urls.API_EVENT_EDIT.format(um_key=um_key)
    data: dict = {
        "appkey": um_key,
        "displayName": display_name or f'暂无描述_{random.randint(0, 1000)}',
        "propertyStatus": "normal",
        "eventType": "calculation",
        "propertyList": [],
        "eventId": event_id,
        "relatedId": um_key,
        "dataSourceId": um_key
    }
    r = requests.post(url=url, headers=get_default_headers(), data=get_post_json(data))
    if is_response_ok(r):
        print(f'修改自定义事件 成功：{display_name} {event_id} {um_key}')
        return True
    else:
        if '事件名称已存在' in eval(r.text).get("msg"):
            return edit_event(um_key=um_key, event_id=event_id, display_name=f'{display_name}_{random.randint(0, 1000)}')
        else:
            print(f'修改自定义事件 失败：{display_name} {event_id} {get_fail_msg(um_key=um_key, r=r)}')
            return False


def is_response_ok(r):
    """
    请求是否成功
    :param r:
    :return:
    """
    try:
        return r and r.status_code == 200 and eval(r.text).get('code') == 200
    except:
        return False


def event_restore(um_key: str, ids: [str]):
    """批量恢复自定义事件"""
    event_restore_or_pause(um_key=um_key, ids=ids, url=urls.API_EVENT_RESTORE.format(um_key=um_key))


def event_restore_bysource(um_key: str, um_key_source: str):
    """
    批量恢复自定义事件，根据指定源进行恢复
    :param um_key:
    :param um_key_source: 源，只有跟此源中的数据匹配，才给恢复显示
    :return:
    """
    json_dict = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}_pause.txt'))
    json_dict_source = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key_source}.txt'))
    source_key_names = ['%s' % item.get('name') for item in json_dict_source.get('data').get('items') or []]
    ids = []
    for item in json_dict.get('data').get('list') or []:
        if item.get('name') in source_key_names:
            ids.append(item.get('eventId'))
    event_restore(um_key=um_key, ids=ids)


def event_pause(um_key: str, ids: [str]):
    """批量暂停自定义事件"""
    event_restore_or_pause(um_key=um_key, ids=ids, url=urls.API_EVENT_PAUSE.format(um_key=um_key))


def event_pause_all(um_key: str):
    """批量暂停所有自定义事件"""
    json_dict = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}.txt'))
    ids = []
    for item in json_dict.get('data').get('items') or []:
        ids.append(item.get('eventId'))
    event_pause(um_key=um_key, ids=ids)


def event_restore_or_pause(um_key: str, ids: [str], url: str):
    """
    恢复/暂停 自定义事件
    :param um_key: 友盟key，每隔应用单独的key
    :param ids: 自定义事件的id列表
    :param url: api 请求地址
    :return:
    """
    tag: str = '批量恢复' if 'restore' in url else '批量暂停'
    if len(ids or []) == 0:
        print(f'需要【{tag}】的eventIds列表为空，跳过。')
        return

    data: dict = {
        "appkey": um_key,
        "eventIds": ids,
        "relatedId": um_key,
        "dataSourceId": um_key
    }
    r = requests.post(url=url, headers=get_default_headers(), data=get_post_json(data))

    if is_response_ok(r):
        print(f'【{tag}】自定义事件 成功，共{len(ids)}条数据：{ids}')
    else:
        print(f'【{tag}】自定义事件 失败:{get_fail_msg(um_key=um_key, r=r)}')


def update_event_multiattribute_to_calculation(um_key: str):
    """
    更新自定义事件-》计算事件
        multiattribute -》 calculation
    :param um_key:
    :return:
    """
    json_dict = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}.txt'))
    json_dict_pause = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}_pause.txt'))
    lst = list(json_dict.get('data').get('items') or []) + list(json_dict_pause.get('data').get('list') or [])
    succeed_count: int = 0
    fail_count: int = 0
    for item in lst or []:
        if 'multiattribute' == item.get('eventType'):
            event_id = item.get('eventId')
            display_name = re.sub(r'[，（()）]', '', item.get('displayName') or '')\
                .replace('/', '_').replace('][', '_').replace('[','').replace(']','')
            print(f'正在更新：{event_id} {display_name}')
            is_succeed = edit_event(um_key=um_key, event_id=event_id, display_name=display_name)
            if is_succeed:
                succeed_count += 1
            else:
                fail_count += 1
            time.sleep(0.1)
    if succeed_count == 0 and fail_count == 0:
        print('暂无需要更新（multiattribute -》 calculation）的数据。')
    else:
        print(f'更新完成：成功{succeed_count}，失败{fail_count}')


def update_event_display_name(um_key: str, um_key_source: str):
    """
    同步更新自定义事件的显示名称，根据指定源进行恢复
    :param um_key:
    :param um_key_source: 源，只有跟此源中的数据匹配 且 显示名称不一样，才给同步更新显示名称
    :return:
    """
    json_dict = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}.txt'))
    json_dict_source = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key_source}.txt'))
    for item in json_dict.get('data').get('items') or []:
        for item_source in json_dict_source.get('data').get('items') or []:
            if item.get('name') == item_source.get('name'):
                if item.get('displayName') != item_source.get('displayName'):
                    # 找出相同key_name自定义事件，并且显示名称不同的，进行更新
                    print(f'显示名称不一致，需要更新：{item.get("displayName")} 变更为==> {item_source.get("displayName")}')
                    edit_event(um_key=um_key, event_id=item.get('eventId'), display_name=item_source.get('displayName'))
                continue


def copy_event(um_key: str, um_key_source: str):
    """
    批量复制 自定义事件
    :param um_key:
    :param um_key_source: 复制源的友盟key
    :return:
    """
    if um_key == um_key_source:
        print('复制操作的两个友盟key相同，中止复制操作。')
        return
    url: str = urls.API_EVENT_COPY.format(um_key=um_key)
    data: dict = {
        "sourceRelatedId": um_key,
        "relatedId": um_key,
        "dataSourceId": um_key_source
    }
    r = requests.post(url=url, headers=get_default_headers(), data=get_post_json(data))
    if is_response_ok(r):
        print(f'批量复制 自定义事件 成功：{um_key_source} -> {um_key}')
    else:
        print(f'批量复制 自定义事件 失败：{get_fail_msg(um_key=um_key, r=r)}')


def get_fail_msg(um_key: str, r):
    """
    获取失败的提示信息
    :param um_key: 当前操作的友盟key
    :param r: 响应体
    :return:
    """
    try:
        return f'{um_key} {eval(r.text).get("msg")}'
    except:
        return f'{um_key}'


def cache_event_list(um_keys):
    """
    根据友盟key获取对应的自定义事件列表最新数据并缓存到本地
    :param um_keys:
    :return:
    """
    for um_key in um_keys or []:
        get_event_list(um_key=um_key)
        get_event_pause_list(um_key=um_key)
