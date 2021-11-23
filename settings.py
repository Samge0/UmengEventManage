#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/25 下午1:45
# @Author  : Samge


# 登录友盟后台，F12 获取的token跟cookie请求信息
CONTENT_TYPE = 'application/json;charset=UTF-8'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
X_XSRF_TOKEN = '320a90c4-4869-4145-9858-708e5a37e71f'  # x-xsrf-token
X_XSRF_TOKEN_HAITANG = '2e989923-7c2d-461a-9c3f-db2ece758c77'  #x-xsrf-token-haitang
COOKIE = 'UM_distinctid=1783a53fdd02a-01b7d2f5803b2a-1e261205-1fa400-1783a53fdd128f; dplus_cross_id=1783a53fdd3261-0dc6c1b34600ca-1e261205-1fa400-1783a53fdd413e; dplus_finger_print=1102023319; cna=EW+6GOctb3gCAXQYZf2EXffk; cn_1273967994_dplus=1%5B%7B%7D%2Cnull%2Cnull%2Cnull%2Cnull%2C%22%24direct%22%2C%221783a53fdd02a-01b7d2f5803b2a-1e261205-1fa400-1783a53fdd128f%22%2C%221615881126%22%2C%22%24direct%22%2C%22%24direct%22%5D; cn_1271885898_dplus=1%5B%7B%22userid%22%3A%22948331124%40qq.com%22%2C%22AppKey%22%3A%2259f935b7b27b0a7776000027%22%7D%2C0%2C1630045940%2C0%2C1630045940%2Cnull%2C%221783a53fdd02a-01b7d2f5803b2a-1e261205-1fa400-1783a53fdd128f%22%2C%221615881315%22%2C%22https%3A%2F%2Fwww.umeng.com%2Fpush%3Facm%3Dlb-zebra-577134-7502775.1003.4.6889757%26scm%3D1003.4.lb-zebra-577134-7502775.OTHER_15820725029761_6889757%22%2C%22www.umeng.com%22%5D; isg=BPj4F-e97XPoQACPlYkz6Kzfya-KYVzr55l2gDJppzPNTZw32nLee1t8B0V9HRTD; uc_session_id=4039f3e5-c2bf-4fc0-b80b-37155eef46fe; XSRF-TOKEN-HAITANG=2e989923-7c2d-461a-9c3f-db2ece758c77; XSRF-TOKEN=320a90c4-4869-4145-9858-708e5a37e71f; umplus_uc_token=1FYcvlILBlq8DEGJOw5KfPg_1c3cb857cd2a410eb9cf2b4f0cb27ac1; umplus_uc_loginid=948331124%40qq.com; Hm_lvt_289016bc8d714b0144dc729f1f2ddc0d=1636523543,1636625848,1636701780,1637301742; aplus-utm-params=%7B%22utm_source%22%3A%22w_bdsemA_Brand_pc_6664%22%2C%22utm_source_time%22%3A1637301742248%7D; _m_h5_c=5789c7e2f1c2aedfd3e689a9673625ef_1637310382244%3Ba2472c1916e9f2cea9468ad92e59dfda; cn_1258498910_dplus=1%5B%7B%22userid%22%3A%22948331124%40qq.com%22%2C%22utm_source%22%3A%22w_bdsemA_Brand_pc_6664%22%2C%22common_is_lt_ie8%22%3A%22N%22%2C%22common_is_spider_hit%22%3A%22N%22%7D%2C0%2C1636973057%2C0%2C1636973057%2C%22www.baidu.com%22%2C%221783a53fdd02a-01b7d2f5803b2a-1e261205-1fa400-1783a53fdd128f%22%2C%221615881255%22%2C%22https%3A%2F%2Fmobile.umeng.com%2F%22%2C%22mobile.umeng.com%22%5D; EGG_SESS=_GOCmDZcFN18IbC7Ny32_kTBV3wkSiguFvx3G5aNhzG9n-Q_wBKF-BqtENDBs2Z4dM2T2KdQYX0jwdAVjXwt7QIdGBqCYGdwn5jDEJn9_RyihOMUct0uX8H7Xx2NeOQw_CjfCxRnTnTtUBcul9M8HA-fncB8Q5_HKgIdgoA0x4a2Kqbr8p9dxrqdToN0EKzQELqVl61ztpMsysMJU_ZkGKk2U6ITOIZToAtV_D9XAzbQOjAHbFlpEIeX8RgIvBX1qczB9Ibu31WgV3p7yY694x7dF9QR9QFs2CLuxbCAbXssHHChvXuLadjtC7CNVe_enceENUwrnXvtZS4ql7xOg4xbYEoyUjmt6tP4iQfCZsml2mbVGH4JNBMZF2CVhZ2YTInPABKCJYq3fWK5X-G8caMEZc2_7Qe1NgEWtaHFBqG7UjUlB8ZMw5NRuaQabezUDX1Hr4y2wxuJ17WeQIVl6G0bcdO-YbC_4hLpXZ3MSVbBnXI3MZqCQ2SFcKIX-CiYIz3Em2W_98M0BC2Ld_7saMsKO-_fsKb25Y5000U6M3jHdkSzmn0V-dIL9cEQANel9nDU0Ra2LHgelDd74h6BsSlwd0oen7ifUVaZmfygp8QTZ8sMU7i1KhAuq2VjIPASWZfCQeqkU3H9jZo62ZL_bQ26a4ToxZaEBg_dhBrohqT9t-C3BVOZMSnpKsTFSA8CgdUkEJMzpG5mbeRjig6Od_wjcXQeNWCa6fasp7d2bIHqsHVbJGhtJG7Q4IGBaIQvk7kwM8nFglBtKsDALuKWJbbhva5taHBFnpt-VHvxFtM=; Hm_lpvt_289016bc8d714b0144dc729f1f2ddc0d=1637301756; cn_1259864772_dplus=1%5B%7B%22UserID%22%3A%22948331124%40qq.com%22%2C%22common_is_lt_ie8%22%3A%22N%22%2C%22common_is_spider_hit%22%3A%22N%22%7D%2C0%2C1636973057%2C0%2C1636973057%2C%22%24direct%22%2C%221783a53fdd02a-01b7d2f5803b2a-1e261205-1fa400-1783a53fdd128f%22%2C%221615881126%22%2C%22%24direct%22%2C%22%24direct%22%5D; CNZZDATA1259864772=1229109645-1615881126-%7C1637296515'


# 主配置的友盟key ：企查猫
UM_KEY_MASTER = '59f935b7b27b0a7776000027'
# 其他需要更新的马甲的友盟key：企查宝（Android）、企业查询宝（Android）的配置
# UM_KEY_SLAVES = ['58df38fe1c5dd037e4000c04']
UM_KEY_SLAVES = ['58df38fe1c5dd037e4000c04', '55c40fc267e58e4e3e0007e4']
