# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : cp_utils.py
   Author   : CoderPig
   date     : 2021-11-18 16:10 
   Desc     : 
-------------------------------------------------
"""
import os
import sys
import importlib
import subprocess


def set_copy_text(content):
    if is_mac():
        p = subprocess.Popen(["pbcopy", "w"], stdin=subprocess.PIPE, close_fds=True)
        p.communicate(input=content.encode("utf-8"))
    else:
        # 动态导包
        module_wcb_str = 'win32clipboard'
        module_wc_str = 'win32con'
        wcb_lib = importlib.import_module(module_wcb_str)
        wc_lib = importlib.import_module(module_wc_str)
        wcb_lib.OpenClipboard()
        wcb_lib.EmptyClipboard()
        wcb_lib.SetClipboardData(wc_lib.CF_UNICODETEXT, content)
        wcb_lib.CloseClipboard()


async def hot_key(page, key1, key2):
    await page.keyboard.down(key1)
    await page.keyboard.press(key2)
    await page.keyboard.up(key1)


# 判断是否为mac
def is_mac():
    return sys.platform.startswith('darwin')


if __name__ == '__main__':
    set_copy_text("哈哈")
