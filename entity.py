# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : entity.py
   Author   : CoderPig
   date     : 2021-11-18 11:20 
   Desc     : 数据实体
-------------------------------------------------
"""


class Article:
    def __init__(self, md_file=None, md_content=None, render_content=None, tags=None, cover_file=None,
                 summary=None, category=None, column=None, title=None):
        """ 初始化方法

        Args:
            md_file: md文件
            md_content: md文件内容
            render_content: 渲染后的文本
            tags: 标签
            cover: 封面
            summary: 摘要
            category: 分类
            column: 专栏
            title: 标题
        """
        self.md_file = md_file
        self.md_content = md_content
        self.render_content = render_content
        self.tags = tags
        self.cover_file = cover_file
        self.summary = summary
        self.category = category
        self.column = column
        self.title = title

    def to_dict(self):
        return {
            'md_file': self.md_file,
            'md_content': self.md_content,
            'render_content': self.render_content,
            'tags': self.tags,
            'cover_file': self.cover_file,
            'summary': self.summary,
            'category': self.category,
            'column': self.column,
            'title': self.title
        }
