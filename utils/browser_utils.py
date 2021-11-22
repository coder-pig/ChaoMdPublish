# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : browser_utils.py
   Author   : CoderPig
   date     : 2021-11-18 14:55 
   Desc     : 
-------------------------------------------------
"""
from pyppeteer import launch, launcher
from pyppeteer_stealth import stealth

default_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 ' \
             'Safari/537.36 '

# chromium启动配置参数
launch_args = [
    "--no-sandbox",  # 非沙盒模式
    "--disable-infobars",  # 隐藏信息栏
    default_ua,
    "--log-level=3",  # 日志等级
    "--start-maximized"  # 窗口最大化模式
]


# 防止WebDriver检测
async def prevent_web_driver_check(page):
    if page is not None:
        # 隐藏webDriver特征
        await page.evaluateOnNewDocument("""() => {
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined })}
        """)
        # 某些站点会为了检测浏览器而调用js修改结果
        await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'lang uages', { get: () => ['en-US', 'en'] }); }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')


# 启动浏览器
async def init_browser(headless=False):
    return await launch({'headless': headless,
                         'args': launch_args,
                         'userDataDir': './userData',
                         'dumpio': True,
                         'ignoreHTTPSErrors ': True})


# 新建页面
async def init_page(browser):
    page = await browser.newPage()
    await page.setViewport({'width': 1960, 'height': 1080})
    await page.setJavaScriptEnabled(True)
    await prevent_web_driver_check(page)
    await stealth(page)
    return page
