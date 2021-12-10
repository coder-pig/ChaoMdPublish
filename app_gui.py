# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : app_gui.py
   Author   : CoderPig
   date     : 2021-12-09 10:29 
   Desc     : 图形化界面
-------------------------------------------------
"""
import json
import os
import re

import PySimpleGUI as sg

import config_getter
from utils import cp_file_utils, task_utils

# sg.theme_previewer()    # 预览所有主题
sg.theme("DarkAmber")  # 设置主题
website_config_json = os.path.join(os.getcwd(), config_getter.get_config(key="website_config_json"))
pos_pattern = re.compile(r'_(\d+)', re.S)
is_login_pattern = re.compile(r'去登陆(\d+)', re.S)


# 程序主页面
def main_gui():
    frame_layout_control = [
        [sg.Text('功能选择', size=[50, 1])],
        [sg.Button('站点管理', key='site_control')],
        [sg.Button('文章发布', key='publish_article')],
        [sg.Button('退出程序', key='exit_app')],
    ]
    window_main = sg.Window('ChaoMD多平台发布工具', frame_layout_control)
    while True:
        event, value = window_main.read()
        if event == 'exit_app' or event == sg.WIN_CLOSED:
            break
        if event == 'site_control':
            site_control()
        if event == 'publish_article':
            print('文章发布')
    window_main.close()


# 站点管理
def site_control():
    # 读取配置选项
    websites = website_dict['website_configs']
    # 生成表头
    web_site_headers = [
        [sg.Text(h, size=(10, 1), pad=((10, 0), 0), text_color='white')
         for h in ['站点', "启用状态", "登录状态", "认证", "账号设置"]]]
    # 添加表头
    frame_layout_site_control = [web_site_headers]
    # 表体控件id
    enable_status_checkbox_ids = []
    login_status_text_ids = []
    to_login_button_ids = []
    account_setting_button_ids = []
    # 添加表内容
    for pos, website in enumerate(websites):
        enable_status_checkbox_id = f"enable_status_checkbox_{pos}"
        login_status_text_id = f"login_status_text_{pos}"
        to_login_button_id = f"to_login_button_{pos}"
        account_setting_button_id = f"account_setting_button_{pos}"
        enable_status_checkbox_ids.append(enable_status_checkbox_id)
        login_status_text_ids.append(login_status_text_id)
        to_login_button_ids.append(to_login_button_id)
        account_setting_button_ids.append(account_setting_button_id)
        frame_layout_site = [
            sg.Text(website['website_name'], size=(10, 1), pad=((8, 0), 0)),
            sg.Checkbox(
                "已启用" if website['is_publish'] else "未启用",
                key=enable_status_checkbox_id, default=website['is_publish'], enable_events=True, size=(8, 1)
            ),
            sg.Text("已登录" if website['is_login'] else "未登录", key=login_status_text_id, size=(8, 1)),
            sg.Button("去登录", key=to_login_button_id, size=(10, 1)),
            sg.Button("配置", key=account_setting_button_id, size=(10, 1)),
        ]
        frame_layout_site_control.append(frame_layout_site)
    window_site_control = sg.Window("站点管理", frame_layout_site_control)
    while True:
        event, value = window_site_control.read()
        if event == sg.WIN_CLOSED:
            cp_file_utils.write_text_to_file(json.dumps(website_dict, ensure_ascii=False), website_config_json)
            break
        else:
            # 复选框逻辑处理
            if event in enable_status_checkbox_ids:
                pos_result = pos_pattern.search(event)
                if pos_result is not None:
                    pos = int(pos_result.group(1))
                    status = window_site_control[event].get()
                    websites[pos]['is_publish'] = status
                    window_site_control[event].update(text="已启用" if status else "未启用")
            # 去登录处理
            if event in to_login_button_ids:
                pos_result = pos_pattern.search(event)
                if pos_result is not None:
                    pos = int(pos_result.group(1))
                    # 判断是否配置账号密码，未配置弹窗告知
                    website = websites[pos]
                    account = website['account']
                    password = website['password']
                    if account is None or len(account) == 0 or password is None or len(password) == 0:
                        sg.popup("请先配置账号密码")
                    # 已配置执行自动登录网站的逻辑，登陆完更新状态
                    else:
                        website['is_login'] = task_utils.auto_login(website)
                        window_site_control[login_status_text_ids[pos]].update("已登录" if website['is_login'] else "未登录")
            # 配置处理
            if event in account_setting_button_ids:
                pos_result = pos_pattern.search(event)
                if pos_result is not None:
                    pos = int(pos_result.group(1))
                    account_setting(pos)
    window_site_control.close()


# 账号设置
def account_setting(pos):
    websites = website_dict['website_configs']
    website = websites[pos]
    account = website['account']
    password = website['password']
    frame_layout_account = [
        [sg.Text("账号", size=(5, 1)), sg.Input(account, key="account", size=(20, 1))],
        [sg.Text("密码", size=(5, 1)), sg.Input(password, key="password", size=(20, 1))],
        [sg.Button("确定", key="account_setting_confirm", size=(10, 1)),
         sg.Button("取消", key="account_setting_cancel", size=(10, 1))]
    ]
    window_account = sg.Window('账号设置', frame_layout_account)
    while True:
        event, value = window_account.read()
        if event == sg.WIN_CLOSED or event == "account_setting_cancel":
            break
        elif event == "account_setting_confirm":
            website['account'] = window_account['account'].get()
            website['password'] = window_account['password'].get()
            cp_file_utils.write_text_to_file(json.dumps(website_dict, ensure_ascii=False), website_config_json)
            break
    window_account.close()


if __name__ == '__main__':
    website_dict = json.loads(cp_file_utils.read_file_text_content(website_config_json))
    main_gui()
