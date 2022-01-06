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

from . import urls
from ..um import file_util

true = True
false = False
null = None

# 友盟的socket通讯对象
um_socks = None
# 请求头
default_headers = {}
# 停止标记
stop = False

# 每次请求友盟api接口后的间隔时间，单位：秒
SLEEP_TIME = 1

# log长度截断的字符长度
LOG_LEN = 300


def update_um_data(um_key: str, um_key_master: str):
    """
    更新友盟 自定义事件 数据
    :param um_key: 要更新的友盟key
    :param um_key_master: 源友盟key
    :return:
    """
    _print_tip(f'\n\n==============>>正在更新：{um_key}')
    time.sleep(SLEEP_TIME)

    # _print_tip(f'\n==============>>（非必须）修改某些占位自定义事件的显示名称：{um_key}')
    # key_word = 'ID_CompanyDes_'  # 这里的关键词根据业务需要自定义
    # update_display_name_to_key_name(um_key=um_key, key_word=key_word)
    # time.sleep(SLEEP_TIME)

    _print_tip(f'\n==============>>1、导出友盟自定义事件【源】：{um_key_master}')
    export_event(um_key=um_key_master)
    time.sleep(SLEEP_TIME)

    _print_tip(f'\n==============>>2、暂停所有自定义事件：{um_key}')
    event_pause_all(um_key=um_key)
    time.sleep(SLEEP_TIME)

    _print_tip('\n==============>>3、上传/导入友盟自定义事件')
    upload_event(um_key=um_key, file_path=f'{get_temp_file_dir()}/um_keys_{um_key_master}.txt')
    time.sleep(SLEEP_TIME)

    _print_tip(f'\n==============>>4、再次暂停所有自定义事件：{um_key}')
    event_pause_all(um_key=um_key)
    time.sleep(SLEEP_TIME)

    # 重新下载最新的友盟自定义事件并覆盖本地缓存
    refresh_local_file(um_key=um_key, step_tip=5)

    _print_tip(f'\n==============>>6、批量恢复自定义事件，根据指定源进行恢复： {um_key_master} 恢复到==》{um_key}')
    event_restore_by_source(um_key=um_key, um_key_master=um_key_master)
    time.sleep(SLEEP_TIME)

    # 重新下载最新的友盟自定义事件并覆盖本地缓存
    refresh_local_file(um_key=um_key, step_tip=7)

    # _print_tip(f'\n==============>>8、更新自定义事件-》计算事件（calculation）：{um_key}  此步骤非必要，部分产品需要用到')
    # update_event_multiattribute_to_calculation(um_key=um_key)
    # time.sleep(SLEEP_TIME)

    _print_tip(f'\n==============>>8、同步更新自定义事件的显示名称：{um_key_master} 同步到==》{um_key}')
    update_event_display_name(um_key=um_key, um_key_master=um_key_master)
    time.sleep(SLEEP_TIME)

    # 重新下载最新的友盟自定义事件并覆盖本地缓存
    refresh_local_file(um_key=um_key, step_tip=9)

    _print_tip(f'==============>>所有操作已完成：{um_key}\n 点击 https://mobile.umeng.com/platform/{um_key}/setting/event/list 查看')


def add_or_update_event_by_file(um_key: str, file_path: str=None):
    """
    添加自定义事件
        如果自定义事件已存在，则自动更新自定义事件显示名

        文件内容格式（一个自定义事件一行）：友盟key名,描述名字,自定义事件类型（0或1）
        例如：

        ID_Click_Home_XX,首页_点击XX,1
        ID_Click_Home_YY,首页_点击YY,1

    :param um_key:
    :param file_path: 新增的友盟key文件路径，如果不传，则默认读取：{get_temp_file_dir()}/um_keys_new_add.txt
    :return:
    """

    # 获取当前已存在的友盟id，用于判断更新
    json_dict = get_eval_dict(file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key}.txt') or '{}')
    json_dict_pause = get_eval_dict(
        file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key}_pause.txt') or '{}')
    lst = list(get_event_list(json_dict=json_dict)) + list(get_event_list(json_dict=json_dict_pause))
    curr_keys = ["%s" % item.get('name') for item in lst]

    # 获取要新增的友盟事件信息, 用于跟上面列表对比，进行插入或更新
    if not file_path:
        file_path = f'{get_temp_file_dir()}/um_keys_new_add.txt'
    event_list = (file_util.read_txt_file(file_path) or '').split('\n')

    for new_event_line in event_list or []:

        # 判断数据有效性
        if not new_event_line or ',' not in new_event_line:
            continue
        new_event_split_list = new_event_line.split(',')
        if not new_event_split_list or len(new_event_split_list) < 3:
            continue

        # 读取 id、显示名称、类型
        key_name: str = new_event_split_list[0].replace(" ", "")
        display_name: str = new_event_split_list[1].replace(" ", "")
        eventType: str = get_event_type_str(new_event_split_list[2].replace(" ", ""))

        if key_name in curr_keys:
            _print_tip("id已存在，更新显示名")
            for item in lst:
                if key_name == item.get('name'):
                    tip: str = f'id已存在【{key_name}】，更新显示名：{ item.get("displayName")} 变更为==> {display_name}' \
                               f' ， 更新事件类型：{ item.get("eventType")} 变更为==> {eventType}'
                    _print_tip(tip)
                    edit_event(
                        um_key=um_key,
                        event_id=item.get('eventId'),
                        display_name=display_name,
                        eventType=eventType
                    )
                    time.sleep(SLEEP_TIME)
                    break
        else:
            _print_tip(f"id不存在，进行插入：id值：{key_name} ， 显示名称： {display_name}")
            add_event(
                um_key=um_key,
                key_name=key_name,
                display_name=display_name,
                eventType=eventType
            )
            time.sleep(SLEEP_TIME)


def get_event_type_str(v) -> str:
    """
    获取友盟自定义事件类型的 字符串
    :param v:
    :return:
    """
    return 'multiattribute' if v == '0' else 'calculation'


def get_event_type_int(v) -> int:
    """
    获取友盟自定义事件类型的 int 类型
    :param v:
    :return:
    """
    return 0 if v == 'multiattribute' else 1


def refresh_local_file(um_key: str, step_tip: int):
    """
    重新下载最新的友盟自定义事件并覆盖本地缓存
    :param um_key:
    :param step_tip: 任务步骤提示消息，可忽略
    :return:
    """
    _print_tip(f'\n==============>>{step_tip}、重新拉取自定义事件状态列表：{um_key}')
    cache_event_list(um_keys=[um_key])
    time.sleep(SLEEP_TIME)


def query_event_analysis_list(um_key: str):
    """
    获取自定义事件列表（有效的 & 统计今天&昨天的消息数）

        sortBy: 排序方式：
                name=根据友盟自定义事件key名称排序，
                countToday=根据今天消息数排序，
                countYesterday=根据昨日消息数排序，
                deviceYesterday=根据昨日独立设备数排序，

        sortType：
                desc=降序
                asc=升序

    :param um_key: 友盟key，每隔应用单独的key
    :return:
    """
    url: str = urls.API_EVENT_ANALYSIS_LIST.format(BASE_URL=urls.BASE_URL, um_key=um_key)
    data: dict = {
        "relatedId": um_key,
        "sortBy": "deviceYesterday",
        "sortType": "desc",
        "version": "",
        "status": "normal",
        "page": 1,
        "pageSize": 2000,
        "dataSourceId": um_key,
        "version": ""
    }
    r = do_post(url, data)
    if is_response_ok(r):
        _print_tip(f'获取自定义事件列表（有效的 & 统计今天&昨天的消息数）成功：{um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
        file_util.save_txt_file(r.text, f'{get_temp_file_dir()}/analysis_event_lst_{um_key}.txt')
    else:
        _print_tip(f'获取自定义事件列表（有效的 & 统计今天&昨天的消息数）失败：{get_fail_msg(um_key=um_key, r=r)}')


def get_all_events_with_analysis(um_key: str):
    """
    获取所有友盟自定义事件 & 附带消息同级数量
    :param um_key:
    :return:
    """
    json_dict = get_eval_dict(file_util.read_txt_file(f'{get_temp_file_dir()}/analysis_event_lst_{um_key}.txt') or '{}')
    json_dict_pause = get_eval_dict(
        file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key}_pause.txt') or '{}')
    lst = list(get_event_list(json_dict=json_dict)) + list(get_event_list(json_dict=json_dict_pause))
    temp_list = []
    for item in lst:
        temp_list.append({
            'um_key': um_key,
            'um_eventId': item.get('eventId'),
            'um_name': item.get('name'),
            'um_displayName': item.get('displayName'),
            'um_status': item.get('status'),
            'um_eventType': item.get('eventType'),
            'um_eventType_int': get_event_type_int(item.get('eventType')),
            'um_countToday': item.get('countToday') or 0,
            'um_countYesterday': item.get('countYesterday') or 0,
            'um_deviceYesterday': item.get('deviceYesterday') or 0
        })
    return temp_list


def query_app_list() -> (list, str, int):
    """
    获取友盟应用列表
    :return: lst, msg, code
    """
    r = requests.get(url=urls.API_APP_LIST.format(BASE_URL=urls.BASE_URL), headers=get_default_headers())
    # 是否友盟的示例列表，因为没有登录的情况下，友盟会返回自己的示例列表，如果是这种情况，则返回空数组
    is_demo_data: bool = '5f6960d2b473963242a3b459' in r.text \
                         or '5b8cf21af43e481aea000022' in r.text \
                         or '5f6d566180455950e496e0e7' in r.text \
                         or '5f69610ba4ae0a7f7d09d36d' in r.text
    if is_response_ok(r):
        if is_demo_data:
            return [], '请先登录友盟账号并更新cookie的配置信息', 403
        _print_tip(f'获取友盟应用列表 成功：\n【响应结果】：{r.text[:LOG_LEN]}......')
        return get_eval_dict(r.text).get('data'), '获取成功', 200
    else:
        msg: str = get_fail_msg(um_key="", r=r)
        _print_tip(f'获取友盟应用列表 失败：{msg}')
        return [], msg, 400


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
    r = do_post(url, data)
    if is_response_ok(r):
        _print_tip(f'获取自定义事件列表（有效的）成功：{um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
        file_util.save_txt_file(r.text, f'{get_temp_file_dir()}/event_lst_{um_key}.txt')
    else:
        _print_tip(f'获取自定义事件列表（有效的）失败：{get_fail_msg(um_key=um_key, r=r)}')


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
    r = do_post(url, data)
    if is_response_ok(r):
        _print_tip(f'获取自定义事件列表（暂停的）成功：{um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
        file_util.save_txt_file(r.text, f'{get_temp_file_dir()}/event_lst_{um_key}_pause.txt')
    else:
        _print_tip(f'获取自定义事件列表（暂停的）失败：{get_fail_msg(um_key=um_key, r=r)}')


def edit_event(um_key: str, event_id: str, display_name: str, eventType: str):
    """
    修改 自定义事件
    :param um_key: 友盟key，每隔应用单独的key
    :param event_id: 自定义事件id
    :param display_name: 自定义事件显示的名称
    :param eventType: 自定义事件类型
    :return:
    """
    url: str = urls.API_EVENT_EDIT.format(BASE_URL=urls.BASE_URL, um_key=um_key)
    data: dict = {
        "appkey": um_key,
        "displayName": display_name or f'暂无描述_{random.randint(0, 1000)}',
        "propertyStatus": "normal",
        "eventType": eventType,
        "propertyList": [],
        "eventId": event_id,
        "relatedId": um_key,
        "dataSourceId": um_key
    }
    r = do_post(url, data)
    if is_response_ok(r):
        _print_tip(f'修改自定义事件 成功：{display_name} {event_id} {um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
        return True
    else:
        if '事件名称已存在' in get_eval_dict(r.text).get("msg"):
            return edit_event(
                um_key=um_key,
                event_id=event_id,
                display_name=f'{display_name}_{random.randint(0, 1000)}',
                eventType=eventType
            )
        else:
            _print_tip(f'修改自定义事件 失败：{display_name} {event_id} {get_fail_msg(um_key=um_key, r=r)}')
            return False


def add_event(um_key: str, key_name: str, display_name: str, eventType: str):
    """
    添加 自定义事件
    :param um_key: 友盟key，每隔应用单独的key
    :param key_name: 自定义事件的名
    :param display_name: 自定义事件显示的名称
    :return:
    """
    if not key_name:
        _print_tip("自定义事件的key名不能为空")
        raise ValueError("自定义事件的key名不能为空")
    url: str = urls.API_EVENT_ADD.format(BASE_URL=urls.BASE_URL, um_key=um_key)
    data: dict = {
        "appkey": um_key,
        "displayName": display_name or f'暂无描述_{um_key}',
        "name": key_name,
        "eventType": eventType,
        "relatedId": um_key,
        "dataSourceId": um_key
    }
    r = do_post(url, data)
    if is_response_ok(r):
        _print_tip(f'添加自定义事件 成功：{display_name} {key_name} {um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
        return True
    else:
        if '事件名称已存在' in get_eval_dict(r.text).get("msg"):
            return edit_event(
                um_key=um_key,
                key_name=key_name,
                display_name=f'{display_name}_{random.randint(0, 1000)}',
                eventType=eventType
            )
        else:
            _print_tip(f'添加自定义事件 失败：{display_name} {key_name} {get_fail_msg(um_key=um_key, r=r)}')
            return False


def is_response_ok(r):
    """
    请求是否成功
    :param r:
    :return:
    """
    try:
        return r and r.status_code == 200 and get_eval_dict(r.text).get('code') == 200
    except:
        return False


def event_restore(um_key: str, ids: [str]):
    """批量恢复自定义事件"""
    event_restore_or_pause(um_key=um_key, ids=ids, url=urls.API_EVENT_RESTORE.format(BASE_URL=urls.BASE_URL, um_key=um_key))


def event_restore_by_source(um_key: str, um_key_master: str):
    """
    批量恢复自定义事件，根据指定源进行恢复
    :param um_key:
    :param um_key_master: 源，只有跟此源中的数据匹配，才给恢复显示
    :return:
    """
    json_dict = get_eval_dict(file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key}_pause.txt') or '{}')
    json_dict_source = get_eval_dict(file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key_master}.txt') or '{}')
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
    json_dict = get_eval_dict(file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key}.txt') or '{}')
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
        _print_tip(f'需要【{tag}】的eventIds列表为空，跳过。')
        return

    data: dict = {
        "appkey": um_key,
        "eventIds": ids,
        "relatedId": um_key,
        "dataSourceId": um_key
    }
    r = do_post(url, data)
    if is_response_ok(r):
        _print_tip(f'【{tag}】自定义事件 成功，共{len(ids)}条数据：{ids[:5]}...] \n【响应结果】：{r.text[:LOG_LEN]}......')
    else:
        _print_tip(f'【{tag}】自定义事件 失败:{get_fail_msg(um_key=um_key, r=r)}')


def update_event_multiattribute_to_calculation(um_key: str):
    """
    更新自定义事件-》计算事件
        multiattribute -》 calculation
    :param um_key:
    :return:
    """
    json_dict = get_eval_dict(file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key}.txt') or '{}')
    json_dict_pause = get_eval_dict(file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key}_pause.txt') or '{}')
    lst = list(get_event_list(json_dict=json_dict)) + list(get_event_list(json_dict=json_dict_pause))
    succeed_count: int = 0
    fail_count: int = 0
    for item in lst or []:
        if 'multiattribute' == item.get('eventType'):
            event_id = item.get('eventId')
            display_name = re.sub(r'[，（()）]', '', item.get('displayName') or '')\
                .replace('/', '_').replace('][', '_').replace('[', '').replace(']', '')
            _print_tip(f'正在更新：{event_id} {display_name}')
            is_succeed = edit_event(um_key=um_key, event_id=event_id, display_name=display_name)
            if is_succeed:
                succeed_count += 1
            else:
                fail_count += 1
            time.sleep(0.2)
    if succeed_count == 0 and fail_count == 0:
        _print_tip('暂无需要更新（multiattribute -》 calculation）的数据。')
    else:
        _print_tip(f'更新完成：成功{succeed_count}，失败{fail_count}')


def update_event_display_name(um_key: str, um_key_master: str):
    """
    同步更新自定义事件的显示名称，根据指定源进行恢复
    :param um_key:
    :param um_key_master: 源，只有跟此源中的数据匹配 且 显示名称不一样，才给同步更新显示名称
    :return:
    """
    json_dict = get_eval_dict(file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key}.txt') or '{}')
    json_dict_source = get_eval_dict(file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key_master}.txt') or '{}')
    for item in get_event_list(json_dict=json_dict):
        for item_source in get_event_list(json_dict=json_dict_source):
            if item.get('name') == item_source.get('name'):
                # 找出相同key_name自定义事件，并且显示名称不同/类型不同的，进行更新
                need_update_name: bool = item.get('displayName') != item_source.get('displayName')
                need_update_type: bool = item.get('eventType') != item_source.get('eventType')
                if need_update_name:
                    _print_tip(f'显示名称不一致，需要更新：{item.get("displayName")} 变更为==> {item_source.get("displayName")}')
                if need_update_type:
                    _print_tip(f'事件类型不一致，需要更新：{item.get("eventType")} 变更为==> {item_source.get("eventType")}')
                if need_update_name or need_update_type:
                    edit_event(
                        um_key=um_key,
                        event_id=item.get('eventId'),
                        display_name=item_source.get('displayName'),
                        eventType=item_source.get('eventType')
                    )


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
    json_dict = get_eval_dict(file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key}.txt') or '{}')
    json_dict_pause = get_eval_dict(
        file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key}_pause.txt') or '{}')
    lst = list(get_event_list(json_dict=json_dict)) + list(get_event_list(json_dict=json_dict_pause))
    for item in lst:
        key_name: str = item.get('name')
        display_name: str = item.get("displayName")
        eventType: str = item.get("eventType")
        if key_word in key_name and key_name != display_name:
            _print_tip(f'将显示名称改为key的名称：{display_name} 变更为==> {key_name}')
            edit_event(
                um_key=um_key,
                event_id=item.get('eventId'),
                display_name=key_name,
                eventType=eventType
            )


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


def copy_event(um_key: str, um_key_master: str):
    """
    批量复制 自定义事件
    :param um_key:
    :param um_key_master: 复制源的友盟key
    :return:
    """
    if um_key == um_key_master:
        _print_tip('复制操作的两个友盟key相同，中止复制操作。')
        return
    url: str = urls.API_EVENT_COPY.format(BASE_URL=urls.BASE_URL, um_key=um_key)
    data: dict = {
        "sourceRelatedId": um_key,
        "relatedId": um_key,
        "dataSourceId": um_key_master
    }
    r = do_post(url, data)
    if is_response_ok(r):
        _print_tip(f'批量复制 自定义事件 成功：{um_key_master} -> {um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
    else:
        _print_tip(f'批量复制 自定义事件 失败：{get_fail_msg(um_key=um_key, r=r)}')


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
    files = [('file', (f'um_keys.txt', open(file_path, 'rb'), 'text/plain'))]
    headers = {}
    for k, v in get_default_headers().items():
        if 'content-type' != k:
            headers[k] = v
    r = requests.post(url=url, data={}, headers=headers, files=files)
    if is_response_ok(r):
        _print_tip(f'批量导入 自定义事件 成功：{file_path} -> {um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
        return 200, "上传成功"
    else:
        fail_msg: str = get_fail_msg(um_key=um_key, r=r) or "上传失败"
        _print_tip(f'批量导入 自定义事件 失败：{fail_msg}')
        return get_eval_dict(r.text).get('code') or -1, fail_msg


def export_event(um_key: str, file_path: str = None):
    """
    批量导出 自定义事件
    :param um_key:
    :param file_path: 自定义事件文件的保存路径，默认导出到{get_temp_file_dir()}文件目录中
    :return:
    """
    if not file_path:
        file_path = f'{get_temp_file_dir()}/um_keys_{um_key}.txt'
    json_dict = get_eval_dict(file_util.read_txt_file(f'{get_temp_file_dir()}/event_lst_{um_key}.txt') or '{}')
    temp_lst = []
    for item in get_event_list(json_dict=json_dict):
        temp_lst.append(f'{item.get("name")},{item.get("displayName")},{get_event_type_int(item.get("eventType"))}')
    _txt = '\n'.join(temp_lst)
    is_succeed = file_util.save_txt_file(_txt, file_path)
    if is_succeed:
        _print_tip(f'批量导出 自定义事件 成功：{um_key} -> {file_path}')
    else:
        _print_tip(f'批量导出 自定义事件 失败：{um_key}')


def check_um_status(um_key: str):
    """
    检查友盟连接状态
    :param um_key: 友盟key
    :return: True=有效，False=无效
    """
    url: str = urls.API_EVENT_LIST.format(BASE_URL=urls.BASE_URL, um_key=um_key)
    data: dict = {
        "relatedId": um_key,
        "sortBy": "countToday",
        "sortType": "desc",
        "version": "",
        "status": "normal",
        "page": 1,
        "pageSize": 1,
        "dataSourceId": um_key
    }
    r = do_post(url, data)
    if is_response_ok(r):
        return True, '操作成功'
    else:
        return False, get_fail_msg(um_key=um_key, r=r)


def get_fail_msg(um_key: str, r):
    """
    获取失败的提示信息
    :param um_key: 当前操作的友盟key
    :param r: 响应体
    :return:
    """
    try:
        return f'{get_eval_dict(r.text).get("msg")} {um_key}'
    except:
        return f'操作失败 {um_key}'


def cache_event_list(um_keys):
    """
    根据友盟key获取对应的自定义事件列表最新数据并缓存到本地
    :param um_keys:
    :return:
    """
    for um_key in um_keys or []:
        query_event_list(um_key=um_key)
        query_event_pause_list(um_key=um_key)


def cache_analysis_event_list(um_keys):
    """
    根据友盟key获取对应的自定义事件列表最新数据并缓存到本地
    :param um_keys:
    :return:
    """
    for um_key in um_keys or []:
        query_event_analysis_list(um_key=um_key)
        query_event_pause_list(um_key=um_key)


def get_default_headers():
    """
    获取默认的请求头
    :return:
    """
    print(f'default_headers = {default_headers}')
    return default_headers
    # config = settings.get_config()
    # return {
    #     'user-agent': config.get('USER_AGENT'),
    #     'x-xsrf-token': config.get('X_XSRF_TOKEN'),
    #     'x-xsrf-token-haitang': config.get('X_XSRF_HAITANG'),
    #     'content-type': config.get('CONTENT_TYPE'),
    #     'cookie': config.get('COOKIE'),
    # }


def get_post_json(data: dict):
    """
    获取请求体数据
    :param data:
    :return:
    """
    return json.dumps(data, ensure_ascii=False).encode('utf-8')


def get_temp_file_dir():
    """
    获取临时文件的目录
    """
    return f'{os.path.dirname(os.path.realpath(__file__))}/temp_files'
    # return f'./temp_files'


def get_eval_dict(txt: str):
    """
    获取字典
    """
    try:
        return eval(txt) or {}
    except Exception as e:
        tip: str = f'get_eval_dict {txt[:200]}...... 转dict对象失败，e={e[:200]}......'
        _print_tip(tip)
        return {}


def is_exists_pause(um_key: str):
    """
    判断某个友盟key的 暂停事件 缓存文件是否存在
    :param um_key:
    :return:
    """
    return os.path.exists(f'{get_temp_file_dir()}/event_lst_{um_key}_pause.txt')


def is_exists_normal_analysis(um_key: str):
    """
    判断某个友盟key的 有效事件&&附带有统计消息的 缓存文件是否存在
    :param um_key:
    :return:
    """
    return os.path.exists(f'{get_temp_file_dir()}/analysis_event_lst_{um_key}.txt')


def is_exists_normal(um_key: str):
    """
    判断某个友盟key的 有效事件 缓存文件是否存在
    :param um_key:
    :return:
    """
    return os.path.exists(f'{get_temp_file_dir()}/event_lst_{um_key}.txt')


def do_post(url, data):
    """
    进行post请求
    :param url:
    :param data:
    :return:
    """
    return requests.post(url=url, headers=get_default_headers(), data=get_post_json(data))


def _print_tip(tip: str):
    """
    打印提示信息
    :param tip:
    :return:
    """
    if stop:
        raise ValueError("强制退出执行")
    print(tip)
    if um_socks:
        um_socks.send(tip)
