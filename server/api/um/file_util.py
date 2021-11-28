#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/25 下午2:13
# @Author  : Samge
import os


def save_txt_file(_txt, _path, _type='w+'):
    """
    保存文件
    :param _txt: 文本内容
    :param _path: 保存的路径
    :param _type: 文件读写类型，默认 覆盖写
    :return: 成功-True， 失败-False
    """
    try:
        with open(_path, _type, encoding='utf-8') as f:
            f.write(_txt)
            f.flush()
            f.close()
        return True
    except:
        return False


def read_txt_file(_path):
    """
    读取文件
    :param _path: 文件路径
    :return: 成功-返回文件内容， 失败-返回None
    """
    if os.path.exists(_path) is False:
        return None
    with open(_path, "r", encoding='utf-8') as f:  # 打开文件
        data = f.read()
        f.close()
        if data == '':
            return None
        else:
            return data
