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
default_dir = os.path.join(os.getcwd(), config_getter.get_config(key="default_dir"))
input_dir = os.path.join(os.getcwd(), config_getter.get_config(key="input_dir"))
output_dir = os.path.join(os.getcwd(), config_getter.get_config(key="output_dir"))

article_md = os.path.join(input_dir, config_getter.get_config(key="article_md"))
cover_pic = os.path.join(input_dir, config_getter.get_config(key="cover_pic"))
article_config_json = os.path.join(input_dir, config_getter.get_config(key="article_config_json"))
summary = os.path.join(input_dir, config_getter.get_config(key="summary"))

website_config_json = os.path.join(os.getcwd(), config_getter.get_config(key="website_config_json"))
publish_result_file = os.path.join(os.getcwd(), config_getter.get_config(key="publish_result_file"))

# 文章实体
article = None
# 发布列表
publish_list = None


# 初始化日志工具
def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(name)s %(asctime)s %(process)d:%(processName)s- %(levelname)s === (・ω・) → %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S %p")
    logger = logging.getLogger("ChaoMdPublish")
    logger.setLevel(logging.INFO)
    return logger


# 文件检查
def file_check():
    c_logger.info("执行文件完整性校验...")
    if not cp_file_utils.is_dir_existed(default_dir, False):
        c_logger.error("default文件夹不存在，为保证功能完整性，请重新下载此目录...")
        exit(-1)
    cp_file_utils.is_dir_existed(input_dir)
    cp_file_utils.is_dir_existed(output_dir)
    # 检查相关文件是否存在，不存在生成默认文件
    if not cp_file_utils.is_dir_existed(website_config_json, False):
        c_logger.info("检测到网站配置文件不存在，自动创建...")
        cp_file_utils.copy_file(os.path.join(default_dir, config_getter.get_config(key="default_website_config_json")),
                                website_config_json)
    if not cp_file_utils.is_dir_existed(article_md, False):
        c_logger.info("检测到文章md文件不存在，自动创建...")
        cp_file_utils.copy_file(os.path.join(default_dir, config_getter.get_config(key="default_article_md")),
                                article_md)
    if not cp_file_utils.is_dir_existed(cover_pic, False):
        c_logger.info("检测到封面文件不存在，自动创建...")
        cp_file_utils.copy_file(os.path.join(default_dir, config_getter.get_config(key="default_cover_pic")),
                                cover_pic)
    if not cp_file_utils.is_dir_existed(article_config_json, False):
        c_logger.info("检测到文章配置文件不存在，自动创建...")
        cp_file_utils.copy_file(os.path.join(default_dir, config_getter.get_config(key="default_article_config_json")),
                                article_config_json)
    if not cp_file_utils.is_dir_existed(summary, False):
        c_logger.info("检测到摘要文件不存在，自动创建...")
        cp_file_utils.copy_file(os.path.join(default_dir, config_getter.get_config(key="default_summary")),
                                summary)
    c_logger.info("文件完整性校验完毕！！！")


# 文件解析
def file_parsing():
    c_logger.info("开始解析配置文件...")
    # 解析文章和站点配置文件
    temp_article = None
    temp_publish_list = None
    try:
        article_dict = json.loads(cp_file_utils.read_file_text_content(article_config_json))
        temp_article = Article()
        temp_article.md_file = os.path.join(input_dir, article_dict.get('md_file'))
        temp_article.md_content = cp_file_utils.read_file_text_content(temp_article.md_file)
        temp_article.summary = cp_file_utils.read_file_text_content(
            os.path.join(input_dir, article_dict.get('summary_file')))
        temp_article.title = article_dict.get('title')
        temp_article.cover_file = os.path.join(input_dir, article_dict.get('cover_file'))
        temp_article.tags = article_dict.get('tags')
        temp_article.category = article_dict.get('category')
        temp_article.column = article_dict.get('column')

        website_dict = json.loads(cp_file_utils.read_file_text_content(website_config_json))
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
    except json.decoder.JSONDecodeError as jde:
        c_logger.error("配置文件解析异常，请检查后重试！！！")
        c_logger.error("错误信息：{}".format(jde))
        exit(-1)
    except TypeError as te:
        c_logger.error("json文件解析错误，请检查是否存在字段错误，修改后重试！！！")
        exit(-1)
    except Exception as e:
        c_logger.error("其他异常：{}".format(e))
        exit(-1)
    c_logger.info("配置文件解析完毕！！！")
    return temp_article, temp_publish_list


if __name__ == '__main__':
    c_logger = init_logging()
    file_check()
    article, publish_list = file_parsing()
    if article is None:
        c_logger.error("文章配置解析失败，请检查后重试...")
        exit(0)
    if publish_list is None:
        c_logger.error("站点配置解析失败，请检查后重试...")
        exit(0)

    # 遍历获取发布任务
    publish_list = [publish for publish in publish_list if publish.is_publish]

    if len(publish_list) == 0:
        c_logger.info("未检测到需要发布的站点，请修改【website_config.json】中需发布站点的【is_publish】字段为 true")
        exit(0)

    # 获得浏览器
    no_headless_browser = asyncio.get_event_loop().run_until_complete(browser_utils.init_browser())

    # 批量校验登录状态
    check_login_tasks = []
    for publish in publish_list:
        publish.set_article(article)
        publish.set_page(
            page=asyncio.get_event_loop().run_until_complete(browser_utils.init_page(no_headless_browser)))
        check_login_tasks.append(publish.check_is_login())
    asyncio.get_event_loop().run_until_complete(asyncio.wait(check_login_tasks))

    # 遍历未登录站点，执行批量自动登录
    need_login_websites = []
    for publish in publish_list:
        if not publish.is_login:
            need_login_websites.append(publish)
    if len(need_login_websites) == 0:
        c_logger.info("未检出到需要登录的站点...")
    else:
        c_logger.info("检测到需要登录的站点...")
        # 获得有头浏览器
        auto_login_tasks = []
        for need_login_website in need_login_websites:
            need_login_website.set_page(
                page=asyncio.get_event_loop().run_until_complete(browser_utils.init_page(no_headless_browser)))
            auto_login_tasks.append(need_login_website.auto_login())
        asyncio.get_event_loop().run_until_complete(asyncio.wait(auto_login_tasks))

    # 校验登陆完，批量自动发文
    website_publish_tasks = []
    for publish in publish_list:
        publish.set_page(
            page=asyncio.get_event_loop().run_until_complete(browser_utils.init_page(no_headless_browser)))
        website_publish_tasks.append(publish.load_write_page())
    asyncio.get_event_loop().run_until_complete(asyncio.wait(website_publish_tasks))
    c_logger.info("所有文章发布完毕...")
