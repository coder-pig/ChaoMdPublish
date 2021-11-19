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
import win32clipboard as w
import win32con


def set_copy_text(content):
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(win32con.CF_UNICODETEXT, content)
    w.CloseClipboard()


async def hot_key(page, key1, key2):
    await page.keyboard.down(key1)
    await page.keyboard.press(key2)
    await page.keyboard.up(key1)
