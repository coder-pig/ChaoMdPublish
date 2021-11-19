# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : app.py
   Author   : CoderPig
   date     : 2021-11-18 14:55 
   Desc     : 
-------------------------------------------------
"""
import json
import os

import config_getter
from entity import Article
from publish import *
from utils import cp_file_utils, browser_utils
import asyncio

# 相关文件
article_config_json = os.path.join(os.getcwd(), config_getter.get_config(key="article_config_json"))
website_config_json = os.path.join(os.getcwd(), config_getter.get_config(key="website_config_json"))
output_dir = os.path.join(os.getcwd(), config_getter.get_config(key="output_dir"))
publish_result_file = os.path.join(os.getcwd(), config_getter.get_config(key="publish_result_file"))

# 文章实体
article = None
publish_list = None


# 初始化日志工具
def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(name)s %(asctime)s %(process)d:%(processName)s- %(levelname)s === %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S %p")
    logger = logging.getLogger("ChaoMdPublish")
    logger.setLevel(logging.INFO)
    return logger


# 文件解析
def file_parsing():
    c_logger.info("解析配置文件...")
    global article, publish_list
    cp_file_utils.is_dir_existed(output_dir)
    if not cp_file_utils.is_dir_existed(article_config_json, False):
        c_logger.error("{} 文件不存在".format(article_config_json))
        return None, None
    if not cp_file_utils.is_dir_existed(website_config_json, False):
        c_logger.error("{} 文件不存在".format(website_config_json))
        return None, None

    # 解析文章配置文件
    temp_article = None
    article_dict = json.loads(cp_file_utils.read_file_text_content(article_config_json))
    if article_dict is not None:
        temp_article = Article()
        temp_article.md_file = os.path.join(os.getcwd(), article_dict.get('md_file'))
        temp_article.md_content = cp_file_utils.read_file_text_content(temp_article.md_file)
        temp_article.summary = cp_file_utils.read_file_text_content(
            os.path.join(os.getcwd(), article_dict.get('summary_file')))
        temp_article.title = article_dict.get('title')
        temp_article.cover_file = os.path.join(os.getcwd(), article_dict.get('cover_file'))
        temp_article.tags = article_dict.get('tags')
        temp_article.category = article_dict.get('category')
        temp_article.column = article_dict.get('column')
    else:
        c_logger.error("文件【{}】解析异常".format(article_config_json))

    # 解析站点配置文件
    temp_publish_list = None
    website_dict = json.loads(cp_file_utils.read_file_text_content(website_config_json))
    if website_dict is not None:
        website_configs = website_dict.get('website_configs')
        if website_configs is not None and len(website_configs) > 0:
            temp_publish_list = []
            for website in website_configs:
                pb = eval(website.get('publish_class'))(website_name=website.get('website_name'))
                pb.write_page_url = website.get('write_page_url')
                pb.login_url = website.get('login_url')
                pb.account = website.get('account')
                pb.password = website.get('password')
                pb.is_publish = website.get('is_publish')
                temp_publish_list.append(pb)
    else:
        c_logger.error("文件【{}】解析异常".format(website_config_json))

    return temp_article, temp_publish_list


# 浏览器初始化
def init_browser():
    return asyncio.get_event_loop().run_until_complete(browser_utils.init_browser())


if __name__ == '__main__':
    c_logger = init_logging()
    article, publish_list = file_parsing()
    if article is None:
        c_logger.error("文章配置解析失败，请检查后重试...")
        exit(0)
    if publish_list is None:
        c_logger.error("站点配置解析失败，请检查后重试...")
        exit(0)
    c_logger.info("解析配置文件完毕，初始化浏览器与页面")
    # 初始化浏览器
    browser = asyncio.get_event_loop().run_until_complete(browser_utils.init_browser())
    # 任务列表
    tasks = []
    for publish in publish_list:
        if publish.is_publish:
            publish.set_page(page=asyncio.get_event_loop().run_until_complete(browser_utils.init_page(browser)),
                             article=article)
            tasks.append(publish.load_write_page())
    # 协程并发执行
    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
    c_logger.info("所有文章发布完毕...")
