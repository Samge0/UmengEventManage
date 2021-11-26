#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/25 下午1:45
# @Author  : Samge
import json
import os.path
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


def do_um_synchro_task():
    """
    开始执行友盟同步任务
    :return:
    """
    check_env()
    cache_event_list(um_keys=[settings.UM_KEY_MASTER] + list(settings.UM_KEY_SLAVES))
    for um_key in settings.UM_KEY_SLAVES:
        update_um_data(um_key=um_key, um_key_source=settings.UM_KEY_MASTER)


def do_add_or_update_task():
    """
    执行添加/更新友盟自定义事件的任务
    :return:
    """
    check_env()
    cache_event_list(um_keys=[settings.UM_KEY_MASTER] + list(settings.UM_KEY_SLAVES))
    add_or_update_event_by_file(settings.UM_KEY_MASTER)


def update_um_data(um_key: str, um_key_source: str):
    """
    更新友盟 自定义事件 数据
    :param um_key: 要更新的友盟key
    :param um_key_source: 源友盟key
    :return:
    """
    print(f'\n\n正在更新：{um_key}')
    time.sleep(1)

    # print(f'\n（非必须）修改某些占位自定义事件的显示名称：{um_key}')
    # key_word = 'ID_CompanyDes_'  # 这里的关键词根据业务需要自定义
    # update_display_name_to_key_name(um_key=um_key, key_word=key_word)
    # time.sleep(1)

    print(f'\n1、导出友盟自定义事件【源】：{um_key_source}')
    export_event(um_key=settings.UM_KEY_MASTER)
    time.sleep(1)

    print(f'\n2、暂停所有自定义事件：{um_key}')
    event_pause_all(um_key=um_key)
    time.sleep(1)

    print('\n3、上传/导入友盟自定义事件')
    upload_event(um_key=um_key, file_path=f'temp_files/um_keys_{um_key_source}.txt')
    time.sleep(1)

    print(f'\n4、再次暂停所有自定义事件：{um_key}')
    event_pause_all(um_key=um_key)
    time.sleep(1)

    refresh_local_file(um_key=um_key, step_tip=5)

    print(f'\n6、批量恢复自定义事件，根据指定源进行恢复： {um_key_source} 恢复到==》{um_key}')
    event_restore_by_source(um_key=um_key, um_key_source=um_key_source)
    time.sleep(1)

    refresh_local_file(um_key=um_key, step_tip=7)

    print(f'\n8、更新自定义事件-》计算事件（calculation）：{um_key}')
    update_event_multiattribute_to_calculation(um_key=um_key)
    time.sleep(1)

    print(f'\n9、同步更新自定义事件的显示名称：{um_key_source} 同步到==》{um_key}')
    update_event_display_name(um_key=um_key, um_key_source=um_key_source)
    time.sleep(1)

    refresh_local_file(um_key=um_key, step_tip=10)

    print(f'所有操作已完成：{um_key}\n 点击 https://mobile.umeng.com/platform/{um_key}/setting/event/list 查看')


def refresh_local_file(um_key: str, step_tip: int):
    print(f'\n{step_tip}、重新拉取自定义事件状态列表：{um_key}')
    cache_event_list(um_keys=[um_key])
    time.sleep(1)


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


def query_event_list(um_key: str):
    """
    获取自定义事件列表（有效的）
    :param um_key: 友盟key，每隔应用单独的key
    :return:
    """
    url: str = urls.API_EVENT_LIST.format(BASE_URL=urls.BASE_URL, um_key=um_key)
    data: dict = {
        "relatedId": um_key,
        "sortBy": "countToday",
        "sortType": "desc",
        "version": "",
        "status": "normal",
        "page": 1,
        "pageSize": 2000,
        "dataSourceId": um_key
    }
    r = requests.post(url=url, headers=get_default_headers(), data=get_post_json(data))
    if is_response_ok(r):
        print(f'获取自定义事件列表（有效的）成功：{um_key} \n{r.text[:200]}...')
        file_util.save_txt_file(r.text, f'temp_files/event_lst_{um_key}.txt')
    else:
        print(f'获取自定义事件列表（有效的）失败：{get_fail_msg(um_key=um_key, r=r)}')


def query_event_pause_list(um_key: str):
    """
    获取自定义事件列表（暂停的）
    :param um_key: 友盟key，每隔应用单独的key
    :return:
    """
    url: str = urls.API_EVENT_LIST.format(BASE_URL=urls.BASE_URL, um_key=um_key)
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
        print(f'获取自定义事件列表（暂停的）成功：{um_key} \n{r.text[:200]}')
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
    url: str = urls.API_EVENT_EDIT.format(BASE_URL=urls.BASE_URL, um_key=um_key)
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
        print(f'修改自定义事件 成功：{display_name} {event_id} {um_key} \n{r.text[:200]}')
        return True
    else:
        if '事件名称已存在' in eval(r.text).get("msg"):
            return edit_event(um_key=um_key, event_id=event_id, display_name=f'{display_name}_{random.randint(0, 1000)}')
        else:
            print(f'修改自定义事件 失败：{display_name} {event_id} {get_fail_msg(um_key=um_key, r=r)}')
            return False


def add_event(um_key: str, key_name: str, display_name: str):
    """
    添加 自定义事件
    :param um_key: 友盟key，每隔应用单独的key
    :param key_name: 自定义事件的名
    :param display_name: 自定义事件显示的名称
    :return:
    """
    if not key_name:
        raise ValueError("自定义事件的key名不能为空")
    url: str = urls.API_EVENT_ADD.format(BASE_URL=urls.BASE_URL, um_key=um_key)
    data: dict = {
        "appkey": um_key,
        "displayName": display_name or f'暂无描述_{um_key}',
        "name": key_name,
        "eventType": "calculation",
        "relatedId": um_key,
        "dataSourceId": um_key
    }
    r = requests.post(url=url, headers=get_default_headers(), data=get_post_json(data))
    if is_response_ok(r):
        print(f'添加自定义事件 成功：{display_name} {key_name} {um_key} \n{r.text[:200]}')
        return True
    else:
        if '事件名称已存在' in eval(r.text).get("msg"):
            return add_event(um_key=um_key, key_name=key_name, display_name=f'{display_name}_{random.randint(0, 1000)}')
        else:
            print(f'添加自定义事件 失败：{display_name} {key_name} {get_fail_msg(um_key=um_key, r=r)}')
            return False


def add_or_update_event_by_file(um_key: str, file_path: str=None):
    """
    添加自定义事件
        如果自定义事件已存在，则自动更新自定义事件显示名

        文件内容格式（一个自定义事件一行）：友盟key名,描述名字,1
        例如：

        ID_Click_Home_XX,首页_点击XX,1
        ID_Click_Home_YY,首页_点击YY,1

    :param um_key:
    :param file_path: 新增的友盟key文件路径，如果不传，则默认读取：temp_files/um_keys_new_add.txt
    :return:
    """

    # 获取当前已存在的友盟id，用于判断更新
    json_dict = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}.txt'))
    json_dict_pause = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}_pause.txt'))
    lst = list(get_event_list(json_dict=json_dict)) + list(get_event_list(json_dict=json_dict_pause))
    curr_keys = ["%s" % item.get('name') for item in lst]

    # 获取要新增的友盟事件信息, 用于跟上面列表对比，进行插入或更新
    if not file_path:
        file_path = f'temp_files/um_keys_new_add.txt'
    event_list = file_util.read_txt_file(file_path).split('\n')

    for new_event_line in event_list or []:
        if not new_event_line or ',' not in new_event_line:
            continue

        new_event_split_list = new_event_line.split(',')
        if not new_event_split_list or len(new_event_split_list) < 3:
            continue

        key_name = new_event_split_list[0].replace(" ", "")
        display_name = new_event_split_list[1].replace(" ", "")

        if key_name in curr_keys:
            print("id已存在，更新显示名")
            for item in lst:
                if key_name == item.get('name'):
                    print(f'id已存在【{key_name}】，更新显示名：{ item.get("displayName")} 变更为==> {display_name}')
                    edit_event(
                        um_key=um_key,
                        event_id=item.get('eventId'),
                        display_name=display_name
                    )
                    time.sleep(1)
                    break
        else:
            print(f"id不存在，进行插入：{key_name} {display_name}")
            add_event(
                um_key=um_key,
                key_name=key_name,
                display_name=display_name
            )
            time.sleep(1)


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
    event_restore_or_pause(um_key=um_key, ids=ids, url=urls.API_EVENT_RESTORE.format(BASE_URL=urls.BASE_URL, um_key=um_key))


def event_restore_by_source(um_key: str, um_key_source: str):
    """
    批量恢复自定义事件，根据指定源进行恢复
    :param um_key:
    :param um_key_source: 源，只有跟此源中的数据匹配，才给恢复显示
    :return:
    """
    json_dict = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}_pause.txt'))
    json_dict_source = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key_source}.txt'))
    source_key_names = ['%s' % item.get('name') for item in get_event_list(json_dict=json_dict_source)]
    ids = []
    for item in get_event_list(json_dict=json_dict):
        if item.get('name') in source_key_names:
            ids.append(item.get('eventId'))
    event_restore(um_key=um_key, ids=ids)


def event_pause(um_key: str, ids: [str]):
    """批量暂停自定义事件"""
    event_restore_or_pause(um_key=um_key, ids=ids, url=urls.API_EVENT_PAUSE.format(BASE_URL=urls.BASE_URL, um_key=um_key))


def event_pause_all(um_key: str):
    """批量暂停所有自定义事件"""
    json_dict = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}.txt'))
    ids = []
    for item in get_event_list(json_dict=json_dict):
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
        print(f'【{tag}】自定义事件 成功，共{len(ids)}条数据：{ids[:5]}...] \n{r.text[:200]}')
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
    lst = list(get_event_list(json_dict=json_dict)) + list(get_event_list(json_dict=json_dict_pause))
    succeed_count: int = 0
    fail_count: int = 0
    for item in lst or []:
        if 'multiattribute' == item.get('eventType'):
            event_id = item.get('eventId')
            display_name = re.sub(r'[，（()）]', '', item.get('displayName') or '')\
                .replace('/', '_').replace('][', '_').replace('[', '').replace(']', '')
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
    for item in get_event_list(json_dict=json_dict):
        for item_source in get_event_list(json_dict=json_dict_source):
            if item.get('name') == item_source.get('name'):
                if item.get('displayName') != item_source.get('displayName'):
                    # 找出相同key_name自定义事件，并且显示名称不同的，进行更新
                    print(f'显示名称不一致，需要更新：{item.get("displayName")} 变更为==> {item_source.get("displayName")}')
                    edit_event(um_key=um_key, event_id=item.get('eventId'), display_name=item_source.get('displayName'))


def update_display_name_to_key_name(um_key: str, key_word: str):
    """
    将显示名称改为key的名称，
        部分需要遗弃的自定义事件需要这样处理，因为友盟的免费版没有删除自定义事件的操作，只能改名或暂停，应该是为了防止误删或者其他考虑吧
        友盟中，如果 key名 或 显示名称 已存在，则不会进行导入，
        所以如果导入时特别需要注意重名问题，不然导入不成功
    :param um_key:
    :param key_word: 友盟key_name的关键词，包含这关键词的都将其 display_name 改为key_name
    :return:
    """
    if not key_word:
        return
    json_dict = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}.txt'))
    json_dict_pause = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}_pause.txt'))
    lst = list(get_event_list(json_dict=json_dict)) + list(get_event_list(json_dict=json_dict_pause))
    for item in lst:
        key_name: str = item.get('name')
        display_name: str = item.get("displayName")
        if key_word in key_name and key_name != display_name:
            print(f'将显示名称改为key的名称：{display_name} 变更为==> {key_name}')
            edit_event(um_key=um_key, event_id=item.get('eventId'), display_name=key_name)


def get_event_list(json_dict: dict):
    """
    获取请求结果返回的自定义事件列表，
        因为不同api返回的字段名称可能有变化，所以使用该方法统一获取
    :param json_dict:
    :return:
    """
    if not json_dict:
        return []
    return json_dict.get('data').get('items') or json_dict.get('data').get('list') or []


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
    url: str = urls.API_EVENT_COPY.format(BASE_URL=urls.BASE_URL, um_key=um_key)
    data: dict = {
        "sourceRelatedId": um_key,
        "relatedId": um_key,
        "dataSourceId": um_key_source
    }
    r = requests.post(url=url, headers=get_default_headers(), data=get_post_json(data))
    if is_response_ok(r):
        print(f'批量复制 自定义事件 成功：{um_key_source} -> {um_key} \n{r.text[:200]}')
    else:
        print(f'批量复制 自定义事件 失败：{get_fail_msg(um_key=um_key, r=r)}')


def upload_event(um_key: str, file_path: str):
    """
    批量导入/批量上传 自定义事件
    :param um_key:
    :param file_path: 自定义事件文件路径
    :return:
    """
    if not file_path or not os.path.exists(file_path):
        raise ValueError("要导入的文件不存在")
        return
    url: str = urls.API_EVENT_UPLOAD.format(BASE_URL=urls.BASE_URL, um_key=um_key)
    files = [('file', ('um_keys.txt', open(file_path, 'rb'), 'text/plain'))]
    headers = get_default_headers()
    headers['Content-Type'] = None
    r = requests.post(url=url, data={}, headers=headers, files=files)
    if is_response_ok(r):
        print(f'批量导入 自定义事件 成功：{file_path} -> {um_key} \n{r.text[:200]}')
    else:
        print(f'批量导入 自定义事件 失败：{get_fail_msg(um_key=um_key, r=r)}')


def export_event(um_key: str, file_path: str = None):
    """
    批量导出 自定义事件
    :param um_key:
    :param file_path: 自定义事件文件的保存路径，默认导出到temp_files文件目录中
    :return:
    """
    if not file_path:
        file_path = f'temp_files/um_keys_{um_key}.txt'
    json_dict = eval(file_util.read_txt_file(f'temp_files/event_lst_{um_key}.txt'))
    temp_lst = []
    for item in get_event_list(json_dict=json_dict):
        temp_lst.append(f'{item.get("name")},{item.get("displayName")},1')
    _txt = '\n'.join(temp_lst)
    is_succeed = file_util.save_txt_file(_txt, file_path)
    if is_succeed:
        print(f'批量导出 自定义事件 成功：{um_key} -> {file_path}')
    else:
        print(f'批量导出 自定义事件 失败：{um_key}')


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
        query_event_list(um_key=um_key)
        query_event_pause_list(um_key=um_key)


def check_env():
    if not settings.X_XSRF_TOKEN:
        raise ValueError("请先在settings.py中配置 X_XSRF_TOKEN")
    if not settings.X_XSRF_TOKEN_HAITANG:
        raise ValueError("请先在settings.py中配置 X_XSRF_TOKEN_HAITANG")
    if not settings.COOKIE:
        raise ValueError("请先在settings.py中配置 COOKIE")
    if not settings.UM_KEY_MASTER:
        raise ValueError("请先在settings.py中配置 UM_KEY_MASTER")
    if not settings.UM_KEY_SLAVES:
        raise ValueError("请先在settings.py中配置 UM_KEY_SLAVES")
