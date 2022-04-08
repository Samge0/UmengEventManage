#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/25 下午1:45
# @Author  : Samge
import json
import os.path
import random
import re
import shutil
import time

import requests as requests
from django.db.models import Q

from . import urls
from ..models import UmEventModel
from ..um import file_util
from ..utils import u_md5
from ..views import v_config

true = True
false = False
null = None


# 每次请求友盟api接口后的间隔时间，单位：秒
SLEEP_TIME = 1

# log长度截断的字符长度
LOG_LEN = 300

# 起始标记符: 在判断"自定义事件显示名称是否已存在"时使用到
TAG_START = '￥-S-T-A-R-T-￥'
# 结束标记符：在判断"自定义事件显示名称是否已存在"时使用到
TAG_END = '￥-E—N-D-￥'


class UmTask(object):

    # 当前登录的用户id
    u_id = None

    # 友盟的socket通讯对象
    um_socks = None

    # 请求头
    default_headers = {}

    # 停止标记
    stop = False
    
    def __init__(self, u_id=None, um_socks=None):
        self.u_id = u_id
        self.um_socks = um_socks
        self.default_headers = v_config.get_default_headers(u_id=u_id)

    # ---------------------------------------------- 任务操作 start ---------------------------------------------------
    def synchro_um_data(self, um_key: str, um_key_master: str):
        """
        同步友盟 自定义事件 数据
            将 um_key_master 中的事件 同步到目标 um_key 中

        :param um_key: 需要同步的 友盟key
        :param um_key_master: 数据源源的 友盟key
        :return:
        """
        self._print_tip(f'\n\n==============>>正在更新：{um_key}')
        time.sleep(SLEEP_TIME)

        self._print_tip(f'\n==============>>1、导出友盟自定义事件【源】：{um_key_master}')
        self._export_event(um_key=um_key_master)
        time.sleep(SLEEP_TIME)
    
        self._print_tip(f'\n==============>>2、暂停所有自定义事件：{um_key}')
        self._pause_event_all(um_key=um_key)
        time.sleep(SLEEP_TIME)
    
        self._print_tip('\n==============>>3、上传/导入友盟自定义事件')
        self.upload_event(um_key=um_key, file_path=f'{self.get_temp_file_dir()}/um_keys_{um_key_master}.txt')
        time.sleep(SLEEP_TIME)
    
        self._print_tip(f'\n==============>>4、再次暂停所有自定义事件：{um_key}')
        self._pause_event_all(um_key=um_key)
        time.sleep(SLEEP_TIME)
    
        # 重新下载最新的友盟自定义事件并覆盖本地缓存
        self._reload_event_file(um_key=um_key, step_tip=5)
    
        self._print_tip(f'\n==============>>6、批量恢复自定义事件，根据指定源进行恢复： {um_key_master} 恢复到==》{um_key}')
        self._restore_event_by_source(um_key=um_key, um_key_master=um_key_master)
        time.sleep(SLEEP_TIME)
    
        # 重新下载最新的友盟自定义事件并覆盖本地缓存
        self._reload_event_file(um_key=um_key, step_tip=7)

        self._print_tip(f'\n==============>>8、同步更新自定义事件的显示名称：{um_key_master} 同步到==》{um_key}')
        self._update_event_display_name(um_key=um_key, um_key_master=um_key_master)
        time.sleep(SLEEP_TIME)
    
        # 重新下载最新的友盟自定义事件并覆盖本地缓存
        self._reload_event_file(um_key=um_key, step_tip=9)

        # 刷新本地数据库的友盟自定义事件
        self.update_local_db_events(um_key=um_key)
    
        self._print_tip(f'==============>>所有操作已完成：{um_key}\n 点击 https://mobile.umeng.com/platform/{um_key}/setting/event/list 查看')
    
    def add_or_update_event_by_file(self, um_key: str, file_path: str = None):
        """
        添加自定义事件
            如果 【自定义事件】已存在 / 【自定义事件显示名】已存在，则自动更新 【自定义事件显示名】
    
            文件内容格式（一个自定义事件一行）：友盟key名,描述名字,自定义事件类型（0或1）
            例如：
    
            ID_Click_Home_XX,首页_点击XX,1
            ID_Click_Home_YY,首页_点击YY,1
    
        :param um_key:
        :param file_path: 新增的友盟key文件路径，如果不传，则默认读取：{self.get_temp_file_dir()}/um_keys_new_add.txt
        :return:
        """
        # 获取当前已存在的友盟id，用于判断更新
        json_dict = self._get_dict_event_normal(um_key)
        json_dict_pause = self._get_dict_event_pause(um_key)
        lst = list(self._get_event_list(json_dict=json_dict)) + list(self._get_event_list(json_dict=json_dict_pause))
        curr_keys = ["%s" % item.get('name') for item in lst]
    
        # 获取要新增的友盟事件信息, 用于跟上面列表对比，进行插入或更新
        if not file_path:
            file_path = self._get_default_upload_file()
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
            eventType: str = self._get_event_type_str(new_event_split_list[2].replace(" ", ""))
    
            if key_name in curr_keys:
                self._print_tip("id已存在，更新显示名")
                for item in lst:
                    if key_name == item.get('name'):
                        tip: str = f'id已存在【{key_name}】，更新显示名：{ item.get("displayName")} 变更为==> {display_name}' \
                                   f' ， 更新事件类型：{ item.get("eventType")} 变更为==> {eventType}'
                        self._print_tip(tip)
                        self.edit_event(
                            um_key=um_key,
                            event_id=item.get('eventId'),
                            display_name=display_name,
                            eventType=eventType,
                            key_name=key_name
                        )
                        time.sleep(SLEEP_TIME)
                        break
            else:
                self._print_tip(f"id不存在，进行插入：id值：{key_name} ， 显示名称： {display_name}")
                self.add_event(
                    um_key=um_key,
                    key_name=key_name,
                    display_name=display_name,
                    eventType=eventType
                )
                time.sleep(SLEEP_TIME)
    # ---------------------------------------------- 任务操作 end ---------------------------------------------------

    # ------------------------------------------- 自定义事件操作 start -------------------------------------------------
    def edit_event(self, um_key: str, event_id: str, display_name: str, eventType: str, key_name: str):
        """
        修改 自定义事件
        :param um_key: 友盟key，每隔应用单独的key
        :param event_id: 自定义事件id
        :param display_name: 自定义事件显示的名称
        :param eventType: 自定义事件类型
        :param key_name: 自定义事件id名称
        :return:
        """
        url: str = urls.API_EVENT_EDIT.format(BASE_URL=urls.BASE_URL, um_key=um_key)
        display_name: str = self._check_display_name(um_key=um_key, display_name=display_name, key_name=key_name, display_name_lst=None)
        data: dict = {
            "appkey": um_key,
            "displayName": display_name,
            "propertyStatus": "normal",
            "eventType": eventType,
            "propertyList": [{"name": key_name, "displayName": key_name, "propertyType": "string"}],
            "eventId": event_id,
            "relatedId": um_key,
            "dataSourceId": um_key
        }
        r = self._do_post(url, data)
        if self._is_response_ok(r):
            self._print_tip(f'修改自定义事件 成功：{display_name} {key_name} {um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
            return True
        else:
            if self._is_same_display_name(r):
                self._print_tip(f'该事件显示名称已存在，尝试增加随机数后重新修改：{display_name} {event_id} {um_key} \n【相关判断依据：响应结果】：{r.text[:LOG_LEN]}......')
                time.sleep(SLEEP_TIME)
                return self.edit_event(
                    um_key=um_key,
                    event_id=event_id,
                    display_name=self._check_display_name(um_key=um_key, display_name=display_name, key_name=key_name, display_name_lst=None),
                    eventType=eventType,
                    key_name=key_name
                )
            else:
                self._print_tip(f'修改自定义事件 失败：{display_name} {event_id} {self._get_fail_msg(um_key=um_key, r=r)}')
                return False

    def add_event(self, um_key: str, key_name: str, display_name: str, eventType: str):
        """
        添加 自定义事件
        :param um_key: 友盟key，每隔应用单独的key
        :param key_name: 自定义事件的名
        :param display_name: 自定义事件显示的名称
        :return:
        """
        if not key_name:
            self._print_tip("自定义事件的key名不能为空")
            raise ValueError("自定义事件的key名不能为空")
        url: str = urls.API_EVENT_ADD.format(BASE_URL=urls.BASE_URL, um_key=um_key)
        display_name: str = self._check_display_name(um_key=um_key, display_name=display_name, key_name=key_name, display_name_lst=None)
        data: dict = {
            "appkey": um_key,
            "displayName": display_name,
            "name": key_name,
            "eventType": eventType,
            "relatedId": um_key,
            "dataSourceId": um_key
        }
        r = self._do_post(url, data)
        if self._is_response_ok(r):
            self._print_tip(f'添加自定义事件 成功：{display_name} {key_name} {um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
            return True
        else:
            if self._is_same_display_name(r):
                self._print_tip(f'该事件显示名称已存在，尝试增加随机数后重新添加：{display_name} {key_name} {um_key} \n【相关判断依据：响应结果】：{r.text[:LOG_LEN]}......')
                time.sleep(SLEEP_TIME)
                return self.add_event(
                    um_key=um_key,
                    key_name=key_name,
                    display_name=self._check_display_name(um_key=um_key, display_name=display_name, key_name=key_name, display_name_lst=None),
                    eventType=eventType
                )
            else:
                self._print_tip(f'添加自定义事件 失败：{display_name} {key_name} {self._get_fail_msg(um_key=um_key, r=r)}')
                return False

    def restore_event(self, um_key: str, ids: [str]):
        """批量恢复自定义事件"""
        self._restore_or_pause_event(um_key=um_key, ids=ids, url=urls.API_EVENT_RESTORE.format(BASE_URL=urls.BASE_URL, um_key=um_key))

    def pause_event(self, um_key: str, ids: [str]):
        """批量暂停自定义事件"""
        self._restore_or_pause_event(um_key=um_key, ids=ids,
                                     url=urls.API_EVENT_PAUSE.format(BASE_URL=urls.BASE_URL, um_key=um_key))

    def upload_event(self, um_key: str, file_path: str):
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
        for k, v in self._get_default_headers().items():
            if 'content-type' != k:
                headers[k] = v
        r = requests.post(url=url, data={}, headers=headers, files=files)
        if self._is_response_ok(r):
            self._print_tip(f'批量导入 自定义事件 成功：{file_path} -> {um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
            return 200, "上传成功"
        else:
            fail_msg: str = self._get_fail_msg(um_key=um_key, r=r) or "上传失败"
            self._print_tip(f'批量导入 自定义事件 失败：{fail_msg}')
            return self._get_eval_dict(r.text).get('code') or -1, fail_msg

    def down_events(self, um_keys):
        """
        根据友盟key获取对应的自定义事件列表最新数据并缓存到本地
        :param um_keys:
        :return:
        """
        for um_key in um_keys or []:
            self._down_events_normal(um_key=um_key)
            self._down_events_pause(um_key=um_key)
    # ------------------------------------------- 自定义事件操作 end -------------------------------------------------

    # ------------------------------------------- 判断文件是否存在 start -------------------------------------------------
    def get_temp_file_dir(self):
        """
        获取临时文件的目录
        """
        path: str = f'{os.path.dirname(os.path.realpath(__file__))}/temp_files/{self.u_id or 0}'
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def is_exists_pause(self, um_key: str):
        """
        判断某个友盟key的 暂停事件 缓存文件是否存在
        :param um_key:
        :return:
        """
        return os.path.exists(self._get_event_pause_file(um_key=um_key))

    def is_exists_normal_analysis(self, um_key: str):
        """
        判断某个友盟key的 有效事件&&附带有统计消息的 缓存文件是否存在
        :param um_key:
        :return:
        """
        return os.path.exists(self._get_event_analysis_file(um_key=um_key))

    def is_exists_normal(self, um_key: str):
        """
        判断某个友盟key的 有效事件 缓存文件是否存在
        :param um_key:
        :return:
        """
        return os.path.exists(self._get_event_normal_file(um_key=um_key))
    # ------------------------------------------- 判断文件是否存在 end -------------------------------------------------

    # ------------------------------------------ 下载 & 检测状态 & 更新数据库 start --------------------------------------
    def down_um_apps(self) -> (list, str, int):
        """
        获取友盟应用列表
        :return: lst, msg, code
        """
        r = requests.get(url=urls.API_APP_LIST.format(BASE_URL=urls.BASE_URL), headers=self._get_default_headers())
        # 是否友盟的示例列表，因为没有登录的情况下，友盟会返回自己的示例列表，如果是这种情况，则返回空数组
        is_demo_data: bool = '5f6960d2b473963242a3b459' in r.text \
                             or '5b8cf21af43e481aea000022' in r.text \
                             or '5f6d566180455950e496e0e7' in r.text \
                             or '5f69610ba4ae0a7f7d09d36d' in r.text
        if self._is_response_ok(r):
            if is_demo_data:
                return [], '请先登录友盟账号并更新cookie的配置信息', 499
            self._print_tip(f'获取友盟应用列表 成功：\n【响应结果】：{r.text[:LOG_LEN]}......')
            return self._get_eval_dict(r.text).get('data'), '获取成功', 200
        else:
            msg: str = self._get_fail_msg(um_key="", r=r)
            self._print_tip(f'获取友盟应用列表 失败：{msg}')
            return [], msg, 400

    def check_um_status(self, um_key: str):
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
        r = self._do_post(url, data)
        if self._is_response_ok(r):
            return True, '操作成功'
        else:
            msg: str = (self._get_fail_msg(um_key=um_key, r=r) or '') \
                .replace(um_key, '') \
                .replace('重新登录', '重新登录友盟账号，获取并替换新的cookie')
            return False, msg

    def update_local_db_events(self, um_key):
        """
        从远程api拉取数据，并更新本地数据库的友盟自定义事件
        :param um_key:
        :return:
        """
        self._cache_all_events(um_keys=[um_key])
        results: list = list(self._append_all_event_analysis(um_key=um_key))
        self.insert_event(results=results)
    # ------------------------------------------ 下载 & 检测状态 & 更新数据库 end ----------------------------------------

    # ------------------------------------------ 显示名处理 start ----------------------------------------
    def _check_display_name(self, um_key: str, display_name: str, key_name: str, display_name_lst: list = None) -> str:
        """
        检查一个显示名是否符合要求，不符合要求则直接返回一个新的显示名：
            1、如果显示名已经存在 -》 增加随机数后再次检查
            2、如果显示名不存在，则返回 暂无描述_随机码
        :param um_key:
        :param display_name:
        :param key_name:
        :param display_name_lst:
        :return:
        """
        display_name = display_name or '暂无描述'
        display_name_lst: list = display_name_lst or self._get_display_name_list(um_key=um_key) or []
        display_name_str = ''.join(display_name_lst)

        # 判断该key_name对应的【显示名】是否存在
        is_exist: bool = f'{key_name}{TAG_START}{display_name}{TAG_END}' in display_name_lst
        # 该【显示名】存在个数
        is_exist_count: int = display_name_str.count(f'{TAG_START}{display_name}{TAG_END}')

        # 是否需要拦截：当该key_name对应的【显示名】不存在 & 原先列表已存在这个【显示名】
        need_intercept: bool = not is_exist and is_exist_count > 0
        if need_intercept:
            new_display_name: str = f'{display_name}_{random.randint(0, 1000)}'
            self._print_tip(f'该事件显示名称已存在，尝试增加随机数后重新添加：{display_name} => {new_display_name}')
            return self._check_display_name(
                um_key=um_key,
                display_name=new_display_name,
                key_name=key_name,
                display_name_lst=display_name_lst
            )
        else:
            return display_name

    def _is_same_display_name(self, r):
        """
        是否已经存在相同显示名称
        :param r:
        :return:
        """
        temp_dict: dict = self._get_eval_dict(r.text)
        return '事件名称已存在' in temp_dict.get("msg") or temp_dict.get('code') == 2030140000

    def _get_display_name_list(self, um_key: str):
        """
        获取一个友盟应用当前所有的显示名列表
        :param um_key:
        :return:
        """
        json_dict = self._get_dict_event_normal(um_key)
        json_dict_pause = self._get_dict_event_pause(um_key)
        lst = list(self._get_event_list(json_dict=json_dict)) + list(self._get_event_list(json_dict=json_dict_pause))
        return ['%s' % f"{item.get('name')}{TAG_START}{item.get('displayName')}{TAG_END}" for item in lst]

    def _update_event_display_name(self, um_key: str, um_key_master: str):
        """
        同步更新自定义事件的显示名称，根据指定源进行恢复
        :param um_key:
        :param um_key_master: 源，只有跟此源中的数据匹配 且 显示名称不一样，才给同步更新显示名称
        :return:
        """
        json_dict = self._get_dict_event_normal(um_key)
        json_dict_source = self._get_dict_event_normal(um_key_master)
        for item in self._get_event_list(json_dict=json_dict):
            for item_source in self._get_event_list(json_dict=json_dict_source):
                if item.get('name') == item_source.get('name'):
                    # 找出相同key_name自定义事件，并且显示名称不同/类型不同的，进行更新
                    need_update_name: bool = item.get('displayName') != item_source.get('displayName')
                    need_update_type: bool = item.get('eventType') != item_source.get('eventType')
                    if need_update_name:
                        self._print_tip(f'显示名称不一致，需要更新：{item.get("displayName")} 变更为==> {item_source.get("displayName")}')
                    if need_update_type:
                        self._print_tip(f'事件类型不一致，需要更新：{item.get("eventType")} 变更为==> {item_source.get("eventType")}')
                    if need_update_name or need_update_type:
                        self.edit_event(
                            um_key=um_key,
                            event_id=item.get('eventId'),
                            display_name=item_source.get('displayName'),
                            eventType=item_source.get('eventType'),
                            key_name=item.get('name')
                        )
    # ------------------------------------------ 显示名处理 end ----------------------------------------

    # ------------------------------------------ 自定义事件 恢复/暂停 start ----------------------------------------
    def _restore_event_by_source(self, um_key: str, um_key_master: str):
        """
        批量恢复自定义事件，根据指定源进行恢复
        :param um_key:
        :param um_key_master: 源，只有跟此源中的数据匹配，才给恢复显示
        :return:
        """
        json_dict = self._get_dict_event_pause(um_key)
        json_dict_source = self._get_dict_event_normal(um_key_master)
        source_key_names = ['%s' % item.get('name') for item in self._get_event_list(json_dict=json_dict_source)]
        ids = []
        for item in self._get_event_list(json_dict=json_dict):
            if item.get('name') in source_key_names:
                ids.append(item.get('eventId'))
        self.restore_event(um_key=um_key, ids=ids)

    def _pause_event_all(self, um_key: str):
        """批量暂停所有自定义事件"""
        json_dict = self._get_dict_event_normal(um_key)
        ids = []
        for item in self._get_event_list(json_dict=json_dict):
            ids.append(item.get('eventId'))
        self.pause_event(um_key=um_key, ids=ids)
    
    def _restore_or_pause_event(self, um_key: str, ids: [str], url: str):
        """
        恢复/暂停 自定义事件
        :param um_key: 友盟key，每隔应用单独的key
        :param ids: 自定义事件的id列表
        :param url: api 请求地址
        :return:
        """
        tag: str = '批量恢复' if 'restore' in url else '批量暂停'
        if len(ids or []) == 0:
            self._print_tip(f'需要【{tag}】的eventIds列表为空，跳过。')
            return
    
        data: dict = {
            "appkey": um_key,
            "eventIds": ids,
            "relatedId": um_key,
            "dataSourceId": um_key
        }
        r = self._do_post(url, data)
        if self._is_response_ok(r):
            self._print_tip(f'【{tag}】自定义事件 成功，共{len(ids)}条数据：{ids[:5]}...] \n【响应结果】：{r.text[:LOG_LEN]}......')
        else:
            self._print_tip(f'【{tag}】自定义事件 失败:{self._get_fail_msg(um_key=um_key, r=r)}')
    # ------------------------------------------ 自定义事件 恢复/暂停 end ----------------------------------------

    def insert_event(self, results: list):
        """
        将友盟自定义事件插入数据库，改为 bulk_create 方式批量插入
        :param results:
        :return:
        """
        if not results or len(results) == 0:
            return

        self._print_tip('将友盟自定义事件插入数据库')
        um_key: str = results[0].get('um_key')
        curr_date: str = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        # 批量移除表中旧数据
        _q: Q = Q(u_id=self.u_id) & Q(um_key=um_key)
        UmEventModel.objects.filter(_q).delete()

        # 批量插入新数据
        product_list_to_insert = list()
        for item in results or []:
            um_md5: str = u_md5.get_event_md5(self.u_id, item.get('um_eventId'), curr_date)
            key = UmEventModel(um_md5=um_md5)
            key.u_id = self.u_id
            key.um_key = item.get('um_key')[:128]
            key.um_eventId = item.get('um_eventId')[:128]
            key.um_name = item.get('um_name')[:128]
            key.um_displayName = item.get('um_displayName')[:128]
            key.um_status = item.get('um_status') or 0
            key.um_eventType = item.get('um_eventType') or 0
            key.um_countToday = item.get('um_countToday') or 0
            key.um_countYesterday = item.get('um_countYesterday') or 0
            key.um_deviceYesterday = item.get('um_deviceYesterday') or 0
            key.um_date = curr_date
            product_list_to_insert.append(key)
        UmEventModel.objects.bulk_create(product_list_to_insert)
        self._print_tip('自定义事件批量入库/更新完成')

    def _export_event(self, um_key: str, file_path: str = None):
        """
        批量导出 自定义事件
        :param um_key:
        :param file_path: 自定义事件文件的保存路径，默认导出到{self.get_temp_file_dir()}文件目录中
        :return:
        """
        if not file_path:
            file_path = f'{self.get_temp_file_dir()}/um_keys_{um_key}.txt'
        json_dict = self._get_dict_event_normal(um_key)
        temp_lst = []
        for item in self._get_event_list(json_dict=json_dict):
            temp_lst.append(
                f'{item.get("name")},{item.get("displayName")},{self._get_event_type_int(item.get("eventType"))}')
        _txt = '\n'.join(temp_lst)
        is_succeed = file_util.save_txt_file(_txt, file_path)
        if is_succeed:
            self._print_tip(f'批量导出 自定义事件 成功：{um_key} -> {file_path}')
        else:
            self._print_tip(f'批量导出 自定义事件 失败：{um_key}')

    # ------------------------------------------ 下载自定义事件 start ----------------------------------------
    def _down_events_normal(self, um_key: str):
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
        r = self._do_post(url, data)
        if self._is_response_ok(r):
            self._print_tip(f'获取自定义事件列表（有效的）成功：{um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
            file_util.save_txt_file(r.text, self._get_event_normal_file(um_key=um_key))
        else:
            self._print_tip(f'获取自定义事件列表（有效的）失败：{self._get_fail_msg(um_key=um_key, r=r)}')

    def _down_events_pause(self, um_key: str):
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
        r = self._do_post(url, data)
        if self._is_response_ok(r):
            self._print_tip(f'获取自定义事件列表（暂停的）成功：{um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
            file_util.save_txt_file(r.text, self._get_event_pause_file(um_key=um_key))
        else:
            self._print_tip(f'获取自定义事件列表（暂停的）失败：{self._get_fail_msg(um_key=um_key, r=r)}')

    def _down_events_analysis(self, um_key: str):
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
        r = self._do_post(url, data)
        if self._is_response_ok(r):
            self._print_tip(f'获取自定义事件列表（有效的 & 统计今天&昨天的消息数）成功：{um_key} \n【响应结果】：{r.text[:LOG_LEN]}......')
            file_util.save_txt_file(r.text, self._get_event_analysis_file(um_key=um_key))
        else:
            self._print_tip(f'获取自定义事件列表（有效的 & 统计今天&昨天的消息数）失败：{self._get_fail_msg(um_key=um_key, r=r)}')

    def _reload_event_file(self, um_key: str, step_tip: int):
        """
        重新下载最新的友盟自定义事件并覆盖本地缓存
        :param um_key:
        :param step_tip: 任务步骤提示消息，可忽略
        :return:
        """
        self._print_tip(f'\n==============>>{step_tip}、重新拉取自定义事件状态列表：{um_key}')
        self.down_events(um_keys=[um_key])
        time.sleep(SLEEP_TIME)

    def _cache_all_events(self, um_keys):
        """
        从远程api获取对应 友盟key 的最新自定义事件（有效+暂停）并缓存到本地文件
        :param um_keys:
        :return:
        """
        for um_key in um_keys or []:
            self._down_events_analysis(um_key=um_key)
            self._down_events_pause(um_key=um_key)
    # ------------------------------------------ 下载自定义事件 end ----------------------------------------

    # ------------------------------------------ 本地缓存文件转dice/list start ----------------------------------------
    def _get_default_upload_file(self) -> str:
        """
        默认的 新增的友盟key文件路径
        :return:
        """
        return f'{self.get_temp_file_dir()}/um_keys_new_add.txt'

    def _get_event_normal_file(self, um_key: str) -> str:
        return f'{self.get_temp_file_dir()}/event_lst_{um_key}.txt'

    def _get_event_pause_file(self, um_key: str) -> str:
        return f'{self.get_temp_file_dir()}/event_lst_{um_key}_pause.txt'

    def _get_event_analysis_file(self, um_key: str) -> str:
        return f'{self.get_temp_file_dir()}/analysis_event_lst_{um_key}.txt'

    def _get_dict_event_pause(self, um_key) -> dict:
        """
        读取【暂停的】友盟事件字典
        :param um_key:
        :return:
        """
        return self._get_eval_dict(file_util.read_txt_file(self._get_event_pause_file(um_key=um_key)) or '{}')

    def _get_dict_event_normal(self, um_key) -> dict:
        """
        读取【有效的】友盟事件字典
        :param um_key:
        :return:
        """
        return self._get_eval_dict(file_util.read_txt_file(self._get_event_normal_file(um_key=um_key)) or '{}')

    def _get_dict_event_analysis(self, um_key) -> dict:
        """
        读取【有统计信息的】友盟事件字典
        :param um_key:
        :return:
        """
        return self._get_eval_dict(file_util.read_txt_file(self._get_event_analysis_file(um_key=um_key)) or '{}')

    def _get_event_list(self, json_dict: dict):
        """
        获取请求结果返回的自定义事件列表，
            因为不同api返回的字段名称可能有变化，所以使用该方法统一获取
        :param json_dict:
        :return:
        """
        if not json_dict:
            return []
        return json_dict.get('data').get('items') or json_dict.get('data').get('list') or []

    def _append_all_event_analysis(self, um_key: str):
        """
        拼接所有友盟自定义事件 & 附带消息同级数量
        :param um_key:
        :return:
        """
        json_dict = self._get_dict_event_analysis(um_key=um_key)
        json_dict_pause = self._get_dict_event_pause(um_key)
        lst = list(self._get_event_list(json_dict=json_dict)) + list(self._get_event_list(json_dict=json_dict_pause))
        temp_list = []
        for item in lst:
            temp_list.append({
                'um_key': um_key,
                'um_eventId': item.get('eventId'),
                'um_name': item.get('name'),
                'um_displayName': item.get('displayName'),
                'um_status': item.get('status'),
                'um_eventType': self._get_event_type_int(item.get('eventType')),
                'um_countToday': item.get('countToday') or 0,
                'um_countYesterday': item.get('countYesterday') or 0,
                'um_deviceYesterday': item.get('deviceYesterday') or 0
            })
        return temp_list
    # ------------------------------------------ 本地缓存文件转dice/list end ----------------------------------------

    # ------------------------------------------ 网络请求与结果转换 start ----------------------------------------
    def _get_default_headers(self) -> dict:
        """
        获取默认请求头
        :return:
        """
        return self.default_headers

    def _do_post(self, url: str, data: dict):
        """
        进行post请求
        :param url:
        :param data:
        :return:
        """
        return requests.post(url=url, headers=self._get_default_headers(), data=json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _is_response_ok(self, r):
        """
        请求是否成功
        :param r:
        :return:
        """
        try:
            return r and r.status_code == 200 and self._get_eval_dict(r.text).get('code') == 200
        except:
            return False

    def _get_eval_dict(self, txt: str):
        """
        获取字典
        """
        try:
            return eval(txt) or {}
        except Exception as e:
            tip: str = f'_get_eval_dict {txt[:200]}...... 转dict对象失败，e={e[:200]}......'
            self._print_tip(tip)
            return {}

    def _get_fail_msg(self, um_key: str, r):
        """
        获取失败的提示信息
        :param um_key: 当前操作的友盟key
        :param r: 响应体
        :return:
        """
        try:
            return f'{self._get_eval_dict(r.text).get("msg")} {um_key}'
        except:
            return f'操作失败 {um_key}'

    def _get_event_type_str(self, v) -> str:
        """
        获取友盟自定义事件类型的 字符串
        :param v:
        :return:
        """
        return 'multiattribute' if v == '0' else 'calculation'

    def _get_event_type_int(self, v) -> int:
        """
        获取友盟自定义事件类型的 int 类型
        :param v:
        :return:
        """
        return 0 if v == 'multiattribute' else 1
    # ------------------------------------------ 网络请求与结果转换 end ----------------------------------------

    def _print_tip(self, tip: str):
        """
        打印提示信息
        :param tip:
        :return:
        """
        if self.stop:
            raise ValueError("强制退出执行")
        print(tip)
        if self.um_socks:
            self.um_socks.send(tip)

    def clear(self):
        try:
            shutil.rmtree(self.get_temp_file_dir())
            self._print_tip("已清除临时文件 & 临时变量")
        except Exception as e:
            self._print_tip(f"清除临时文件 & 临时变量 失败：{e}")
        self.stop = True
        self.u_id = None
        self.um_socks = None
