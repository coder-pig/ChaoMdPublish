# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : task_utils.py
   Author   : CoderPig
   date     : 2021-12-09 17:12 
   Desc     : 任务工具类
-------------------------------------------------
"""
from publish import *

from utils.browser_utils import init_browser, init_page, close_browser


# 执行自动登录逻辑
def auto_login(website_dict):
    pb = eval(website_dict.get('publish_class'))(
        website_name=website_dict.get('website_name'),
        login_url=website_dict.get('login_url'),
        account=website_dict.get('account'),
        password=website_dict.get('password')
    )
    browser = asyncio.get_event_loop().run_until_complete(init_browser())
    pb.set_page(page=asyncio.get_event_loop().run_until_complete(init_page(browser)))
    asyncio.get_event_loop().run_until_complete(pb.auto_login())
    asyncio.get_event_loop().run_until_complete(close_browser(browser))
    return pb.is_login
