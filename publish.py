# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : publish.py
   Author   : CoderPig
   date     : 2021-11-18 11:30 
   Desc     : 
-------------------------------------------------
"""
import asyncio
import logging

from pyppeteer import errors

from utils import cp_utils


class Publish:
    def __init__(self, website_name=None, write_page_url=None, login_url=None,
                 account=None, password=None, is_publish=True, page=None, article=None, is_login=False):
        """ 抽取发布文章的公有属性

        Args:
            website_name: 站点名
            write_page_url: 发布页url
            login_url: 登录页url
            account: 账号
            password: 密码
            is_publish: 是否发布，默认为True
            page: Pyppeteer 的 Page实例
            is_login: 是否处于登录状态
        """
        self.website_name = website_name
        self.write_page_url = write_page_url
        self.login_url = login_url
        self.account = account
        self.password = password
        self.is_publish = is_publish
        self.page = page
        self.article = article
        self.logger = logging.getLogger(self.website_name)
        self.logger.setLevel(logging.INFO)
        self.is_login = False

    def to_dict(self):
        return {
            'website_name': self.website_name,
            'write_page_url': self.write_page_url,
            'login_url': self.login_url,
            'account': self.account,
            'password': self.password,
            'is_publish': self.is_publish,
            'is_login': self.is_login,
        }

    def set_article(self, article=None):
        self.article = article

    def set_page(self, page):
        self.page = page

    # 检查登录状态
    def check_is_login(self):
        self.logger.info("检查是否登录...")

    # 自动登录
    def auto_login(self):
        self.logger.info("开始自动登录：{}".format(self.login_url))

    # 加载发布页
    def load_write_page(self):
        self.logger.info("加载写文章页：{}".format(self.write_page_url))

    # 内容填充
    def fill_content(self):
        self.logger.info("开始内容填充...")

    # 其他填充
    def fill_else(self):
        self.logger.info("其他内容填充...")

    # 发布
    def publish_article(self):
        self.logger.info("发布文章...")

    # 结果处理
    def deal_result(self):
        self.logger.info("文章发布完毕...")


class JueJinPublish(Publish):
    async def check_is_login(self):
        super().check_is_login()
        try:
            await self.page.goto(self.write_page_url, options={'timeout': 60000})
            await asyncio.sleep(1)
            await self.page.waitForXPath("//nav/div[@class='toggle-btn']", {'visible': 'visible', 'timeout': 3000})
            self.logger.info("处于登录状态...")
            self.is_login = True
        except errors.TimeoutError as e:
            self.logger.error(e)
            self.logger.info("未登录...")
            self.is_login = False
        finally:
            await self.page.close()

    async def auto_login(self):
        super().auto_login()
        try:
            await self.page.goto(self.login_url, options={'timeout': 60000})
            await asyncio.sleep(2)
            login_bt = await self.page.Jx("//button[@class='login-button']")
            await login_bt[0].click()
            prompt_box = await self.page.Jx("//div[@class='prompt-box']/span")
            await prompt_box[0].click()
            account_input = await self.page.Jx("//input[@name='loginPhoneOrEmail']")
            await account_input[0].type(self.account)
            password = await self.page.Jx("//input[@name='loginPassword']")
            await password[0].type(self.password)
            login_btn = await self.page.Jx("//button[@class='btn']")
            await login_btn[0].click()
            self.logger.info("等待用户验证...")
            # 接着超时等待登录按钮消失，提示用户可能要进行登录验证
            await self.page.waitForXPath("//button[@class='login-button']", {'hidden': True, 'timeout': 60000})
            self.logger.info("用户验证成功...")
            self.is_login = True
        except errors.TimeoutError:
            self.logger.info("用户验证失败...")
            self.logger.error("登录超时，请重试...")
            self.is_login = False
        except Exception as e:
            self.logger.error(e)
            self.is_login = False
        finally:
            await self.page.close()

    async def load_write_page(self):
        super().load_write_page()
        await self.page.goto(self.write_page_url, options={'timeout': 60000})
        await asyncio.sleep(2)
        await self.fill_content()

    async def fill_content(self):
        super().fill_content()

        # 设置标题
        title_input = await self.page.Jx("//input[@class='title-input title-input']")
        await title_input[0].type(self.article.title)

        # 填充内容部分
        content_input = await self.page.Jx("//div[@class='CodeMirror-scroll']")
        await content_input[0].click()
        cp_utils.set_copy_text(self.article.md_content)
        await cp_utils.hot_key(self.page, "Control", "KeyA")
        await cp_utils.hot_key(self.page, "Control", "KeyV")

        # 掘金会进行图片压缩处理，要等一下下再进行后续处理
        await asyncio.sleep(3)

        # 选择Markdown主题和代码高亮样式
        md_theme = await self.page.Jx("//div[@bytemd-tippy-path='16']")
        await md_theme[0].hover()
        await asyncio.sleep(1)

        # 选中喜欢的主题，比如：smartblue
        md_theme_choose = await self.page.Jx(
            "//div[@class='bytemd-dropdown-item-title' and text()='{}']".format('smartblue'))
        await md_theme_choose[0].click()

        # 同理选中喜欢的代码样式，比如：androidstudio
        code_theme = await self.page.Jx("//div[@bytemd-tippy-path='17']")
        await code_theme[0].hover()
        await asyncio.sleep(1)

        code_theme_choose = await self.page.Jx(
            "//div[@class='bytemd-dropdown-item-title' and text()='{}']".format('androidstudio'))
        await code_theme_choose[0].click()

        # 补充其他信息
        await self.fill_else()

    async def fill_else(self):
        super().fill_else()

        # 点击发布按钮
        publish_bt = await self.page.Jx("//button[@class='xitu-btn']")
        await publish_bt[0].click()

        # 选中分类
        category_check = await self.page.Jx("//div[@class='item' and text()=' {} ']".format(self.article.category[0]))
        await category_check[0].click()

        # 添加标签
        for tag in self.article.tags[:1]:
            tag_input = await self.page.Jx("//input[@class='byte-select__input']")
            await tag_input[0].type(tag)
            await asyncio.sleep(1)
            # 默认选中第一个
            tag_li = await self.page.Jx("//li[@class='byte-select-option byte-select-option--hover']")
            await tag_li[0].click()

        # 添加封面
        upload_cover = await self.page.Jx("//input[@type='file']")
        await upload_cover[0].uploadFile(self.article.cover_file)
        await asyncio.sleep(2)

        # 填充摘要
        summary_textarea = await self.page.Jx("//textarea[@class='byte-input__textarea']")
        await summary_textarea[0].click()
        cp_utils.set_copy_text(self.article.summary)
        await cp_utils.hot_key(self.page, "Control", "KeyA")
        await cp_utils.hot_key(self.page, "Control", "KeyV")
        await self.publish_article()

    async def publish_article(self):
        super().publish_article()
        publish_btn = await self.page.Jx("//div[@class='btn-container']/button")
        await publish_btn[1].click()
        await asyncio.sleep(3)
        await self.deal_result()

    async def deal_result(self):
        super().deal_result()
        article_node = await self.page.Jx("//div[@class='share-content']/a")
        article_url = await (await article_node[0].getProperty('href')).jsonValue()
        if article_url is not None:
            self.logger.info("文章发布成功╰(*°▽°*)╯，链接：{}".format(article_url))
        else:
            self.logger.info("文章发布失败 o(╥﹏╥)o")


class CSDNPublish(Publish):
    async def check_is_login(self):
        super().check_is_login()
        await self.page.goto(self.login_url, options={'timeout': 30000})
        await asyncio.sleep(2)
        if self.page.url == self.login_url:
            self.logger.info("未登录...")
            self.is_login = False
        else:
            self.logger.info("处于登录状态...")
            self.is_login = True
        await self.page.close()

    async def auto_login(self):
        super().auto_login()
        # CSDN账号密码登录很容易触发防火墙验证，试过延时输入、模拟人输入不行，猜测是有啥回调的JS，先放一放，采用微信扫码登录吧...
        # password_login = await self.page.Jx("//span[text()='密码登录']")
        # await password_login[0].click()
        # inputs = await self.page.Jx("//input[@class='base-input-text']")
        # await inputs[0].type(self.account)
        # await inputs[1].type(self.password)
        # login_bt = await self.page.Jx("//button[@class='base-button']")
        # await login_bt[0].click()
        # self.logger.info("等待用户验证...")
        try:
            await self.page.goto(self.login_url, options={'timeout': 60000})
            self.logger.info("等待扫码登录...")
            # 超时等待登录按钮消失
            await self.page.waitForXPath("//button[@class='base-button']", {'hidden': True, 'timeout': 60000})
            self.logger.info("用户验证成功...")
            await asyncio.sleep(2)
            if self.page.url == self.login_url:
                self.is_login = False
            else:
                self.is_login = True
        except Exception as e:
            self.logger.error(e)
            self.is_login = False
        finally:
            await self.page.close()

    async def load_write_page(self):
        super().load_write_page()
        await self.page.goto(self.write_page_url, options={'timeout': 60000})
        await asyncio.sleep(2)
        await self.fill_content()

    async def fill_content(self):
        super().fill_content()
        # 设置标题
        title_input = await self.page.Jx("//div[@class='article-bar__input-box']/input")
        await title_input[0].click()
        await title_input[0].type(self.article.title)

        # 内容部分不是纯文本输入，点击选中，然后复制粘贴一波~
        content_input = await self.page.Jx("//div[@class='layout__panel layout__panel--editor']")
        await content_input[0].click()
        await content_input[0].click()
        cp_utils.set_copy_text(self.article.md_content)
        await cp_utils.hot_key(self.page, "Control", "KeyA")
        await self.page.keyboard.press("Backspace")
        await asyncio.sleep(1)
        await cp_utils.hot_key(self.page, "Control", "KeyV")
        await asyncio.sleep(1)

        # 填充摘要
        summary_bt = await self.page.Jx("//button[@data-title='摘要']")
        await summary_bt[0].click()
        summary_textarea = await self.page.Jx("//div[@class='form-entry__field']/textarea")
        await summary_textarea[0].click()
        cp_utils.set_copy_text(self.article.summary)
        await cp_utils.hot_key(self.page, "Control", "KeyA")
        await self.page.keyboard.press("Backspace")
        await asyncio.sleep(1)
        await cp_utils.hot_key(self.page, "Control", "KeyV")
        confirm_bt = await self.page.Jx("//div[@class='normal-confirm-btn']")
        await confirm_bt[0].click()

        # 点击发布文章
        await asyncio.sleep(1)
        publish_bt = await self.page.Jx("//button[@class='btn btn-publish']")
        await publish_bt[0].click()
        await self.fill_else()

    async def fill_else(self):
        super().fill_else()

        await asyncio.sleep(1)
        # 添加封面
        radio = await self.page.Jx("//input[@type='radio']")
        await radio[0].click()
        await asyncio.sleep(1)
        upload_cover = await self.page.Jx("//input[@type='file']")
        await upload_cover[1].uploadFile(self.article.cover_file)

        # 添加文章标签，得先干掉默认的，然后一个个输入回车，而且是动态变化的
        while True:
            tag_curs = await self.page.Jx("//i[@class='el-tag__close el-icon-close']")
            if tag_curs is not None and len(tag_curs) > 0:
                await tag_curs[0].click()
            else:
                break
        tag_add = await self.page.Jx("//button[@class='tag__btn-tag']")
        await tag_add[0].click()
        tag_input = await self.page.Jx("//div[@class='el-input el-input--suffix']/input")
        await tag_input[0].click()
        for tag in self.article.tags:
            await self.page.keyboard.type(tag)
            await self.page.keyboard.press('Enter')
        close_bt = await self.page.Jx("//div[@class='mark_selection_box_body']/button")
        await close_bt[0].click()

        # 选中原创
        original_input = await self.page.Jx("//label[text()='原创']")
        await original_input[0].click()
        await asyncio.sleep(2)
        await self.publish_article()

    async def publish_article(self):
        super().publish_article()
        publish_btn = await self.page.Jx("//button[@class='button btn-b-red ml16']")
        await publish_btn[0].click()
        await asyncio.sleep(3)
        await self.deal_result()

    async def deal_result(self):
        super().deal_result()
        article_node = await self.page.Jx("//i[@class='icon-success-font']/parent::a")
        article_url = await (await article_node[0].getProperty('href')).jsonValue()
        if article_url is not None:
            self.logger.info("文章发布成功╰(*°▽°*)╯，链接：{}".format(article_url))
        else:
            self.logger.info("文章发布失败 o(╥﹏╥)o")
        await self.page.close()


class CTO51Publish(Publish):
    async def check_is_login(self):
        super().check_is_login()
        await self.page.goto(self.login_url, options={'timeout': 30000})
        await asyncio.sleep(1)
        if self.page.url == self.login_url:
            self.logger.info("未登录...")
            self.is_login = False
        else:
            self.logger.info("处于登录状态...")
            self.is_login = True
        await self.page.close()

    async def auto_login(self):
        super().auto_login()
        try:
            await self.page.goto(self.login_url, options={'timeout': 60000})
            await asyncio.sleep(2)
            login_type = await self.page.Jx("//div[@title='密码登录']")
            await login_type[0].click()
            await asyncio.sleep(1)
            password_login = await self.page.Jx("//span[text()='密码登录']")
            await password_login[0].click()
            input_account = await self.page.Jx("//input[@id='loginform-username']")
            await input_account[0].type(self.account)
            input_password = await self.page.Jx("//input[@id='loginform-password']")
            await input_password[0].type(self.password)
            input_login = await self.page.Jx("//input[@value='登 录']")
            await input_login[0].click()
            await asyncio.sleep(1)
            # 超时等待登录按钮消失
            await self.page.waitForXPath("//input[@value='登 录']", {'hidden': True, 'timeout': 60000})
            self.logger.info("用户验证成功...")
            self.is_login = True
        except Exception as e:
            self.logger.error(e)
            self.is_login = False
        finally:
            await self.page.close()

    async def load_write_page(self):
        super().load_write_page()
        await self.page.goto(self.write_page_url, options={'timeout': 60000})
        await asyncio.sleep(1)
        await self.fill_content()

    async def fill_content(self):
        super().fill_content()

        # 设置标题
        title_input = await self.page.Jx("//input[@id='title']")
        await title_input[0].click()
        await title_input[0].type(self.article.title)

        # 内容部分不是纯文本输入，点击选中，然后复制粘贴一波~
        content_input = await self.page.Jx("//textarea")
        await content_input[0].click()
        await content_input[0].click()
        cp_utils.set_copy_text(self.article.md_content)
        await cp_utils.hot_key(self.page, "Control", "KeyA")
        await self.page.keyboard.press("Backspace")
        await asyncio.sleep(1)
        await cp_utils.hot_key(self.page, "Control", "KeyV")
        # 点击发布文章
        publish_bt = await self.page.Jx("//button[@class=' edit-submit']")
        await publish_bt[0].hover()
        await publish_bt[0].click()
        await self.fill_else()

    async def fill_else(self):
        super().fill_else()
        await asyncio.sleep(2)
        # 先默认选中移动分类，后续再优化成动态配置
        category_select_item = await self.page.Jx("//span[text()='{}']/parent::div".format("移动开发"))
        await category_select_item[0].click()
        await asyncio.sleep(1)
        android_item = await self.page.Jx("//span[text()='{}']/parent::div".format("Android"))
        await android_item[0].click()
        # 添加文章标签，得先干掉默认的，然后一个个输入回车，而且是动态变化的
        while True:
            tag_curs = await self.page.Jx("//i[@class='iconeditor editorcancel']/parent::a")
            if tag_curs is not None and len(tag_curs) > 0:
                await tag_curs[0].click()
            else:
                break
        tag_input = await self.page.Jx("//input[@id='tag-input']/parent::div")
        await tag_input[0].click()

        for tag in self.article.tags:
            await self.page.keyboard.type(tag)
            await self.page.keyboard.press(',')

        # 输入摘要
        summary = await self.page.Jx("//textarea[@id='abstractData']")
        await summary[0].click()
        cp_utils.set_copy_text(self.article.summary)
        await cp_utils.hot_key(self.page, "Control", "KeyA")
        await self.page.keyboard.press("Backspace")
        await asyncio.sleep(1)
        await cp_utils.hot_key(self.page, "Control", "KeyV")

        # 选择封面
        single_pic = await self.page.Jx("//input[@class='img_type' and @value='1']")
        await single_pic[0].click()
        upload_cover = await self.page.Jx("//div[@class='item upload-img']//input[@type='file']")
        await upload_cover[0].uploadFile(self.article.cover_file)
        await asyncio.sleep(1)
        await self.publish_article()

    async def publish_article(self):
        super().publish_article()
        publish_btn = await self.page.Jx("//button[@class='release']")
        await publish_btn[0].click()
        await asyncio.sleep(5)
        await self.deal_result()

    async def deal_result(self):
        super().deal_result()
        try:
            await self.page.waitForXPath("//a[text()='查看文章']", {'visible': 'visible', 'timeout': 3000})
            article_node = await self.page.Jx("//a[text()='查看文章']")
            article_url = await (await article_node[0].getProperty('href')).jsonValue()
            if article_url is not None:
                self.logger.info("文章发布成功╰(*°▽°*)╯，链接：{}".format(article_url))
            else:
                self.logger.info("文章发布失败 o(╥﹏╥)o")
        except errors.TimeoutError as te:
            self.logger.info("文章发布失败 o(╥﹏╥)o")
            self.logger.error(te)
        except Exception as e:
            self.logger.info("文章发布失败 o(╥﹏╥)o")
            self.logger.error(e)
        finally:
            await self.page.close()


class JianShuPublish(Publish):
    async def check_is_login(self):
        super().check_is_login()
        await self.page.goto(self.login_url, options={'timeout': 60000})
        await asyncio.sleep(1)
        if self.page.url == self.login_url:
            self.logger.info("未登录...")
            self.is_login = False
        else:
            self.logger.info("处于登录状态...")
            self.is_login = True
        await self.page.close()

    async def auto_login(self):
        super().auto_login()
        try:
            await self.page.goto(self.login_url, options={'timeout': 60000})
            await asyncio.sleep(2)
            input_account = await self.page.Jx("//input[@id='session_email_or_mobile_number']")
            await input_account[0].type(self.account)
            input_password = await self.page.Jx("//input[@id='session_password']")
            await input_password[0].type(self.password)
            input_login = await self.page.Jx("//button[@class='sign-in-button']")
            await input_login[0].click()
            # 简书验证有两步，除了点击文字验证码外，还有短线验证码，所以这里验证两次
            await self.page.waitForXPath("//button[@class='sign-in-button']", {'hidden': True, 'timeout': 30000})
            await asyncio.sleep(5)
            await self.page.waitForXPath("//button[@class='sign-in-button']", {'hidden': True, 'timeout': 30000})
            self.logger.info("用户验证成功...")
            self.is_login = True
        except errors.TimeoutError:
            self.logger.info("用户验证失败...")
            self.logger.error("登录超时，请重试...")
            self.is_login = False
        except Exception as e:
            self.logger.error(e)
            self.is_login = False
        finally:
            await self.page.close()

    async def load_write_page(self):
        super().load_write_page()
        await self.page.goto(self.write_page_url, options={'timeout': 60000})
        await self.page.waitForNavigation()
        new_article = await self.page.Jx("//i[@class='fa fa-plus-circle']/parent::div")
        await new_article[0].click()
        await asyncio.sleep(1)
        await self.fill_content()

    async def fill_content(self):
        # 设置标题
        input_title = await self.page.Jx("//textarea/preceding-sibling::input")
        await input_title[0].click()
        await cp_utils.hot_key(self.page, "Control", "KeyA")
        await self.page.keyboard.press("Backspace")
        await asyncio.sleep(1)
        await input_title[0].type(self.article.title)
        await asyncio.sleep(1)

        # 内容部分不是纯文本输入，点击选中，然后复制粘贴一波~
        content_input = await self.page.Jx("//textarea")
        await content_input[0].click()
        cp_utils.set_copy_text(self.article.md_content)
        await cp_utils.hot_key(self.page, "Control", "KeyA")
        await self.page.keyboard.press("Backspace")
        await asyncio.sleep(1)
        await cp_utils.hot_key(self.page, "Control", "KeyV")
        await asyncio.sleep(2)
        await self.fill_else()

    async def fill_else(self):
        super().fill_else()
        await self.publish_article()

    async def publish_article(self):
        super().publish_article()
        # 发布文章
        publish_article = await self.page.Jx("//a[@data-action='publicize']")
        await publish_article[0].click()
        await asyncio.sleep(1)
        await self.deal_result()

    async def deal_result(self):
        super().deal_result()
        try:
            await self.page.waitForXPath("//a[contains(text(), '发布成功')]", {'visible': 'visible', 'timeout': 3000})
            article_node = await self.page.Jx("//a[contains(text(), '发布成功')]")
            article_url = await (await article_node[0].getProperty('href')).jsonValue()
            if article_url is not None:
                self.logger.info("文章发布成功╰(*°▽°*)╯，链接：{}".format(article_url))
            else:
                self.logger.info("文章发布失败 o(╥﹏╥)o")
        except errors.TimeoutError:
            if self.write_page_url in self.page.url:
                self.logger.info("超过每天发布上限(2篇)，文章发布失败 o(╥﹏╥)o")
        except Exception as e:
            self.logger.info("文章发布失败 o(╥﹏╥)o")
            self.logger.error(e)
        finally:
            await self.page.close()


class ZhiHuPublish(Publish):
    async def check_is_login(self):
        super().check_is_login()
        await self.page.goto(self.login_url, options={'timeout': 60000})
        await asyncio.sleep(1)
        if self.page.url == self.login_url:
            self.logger.info("未登录...")
            self.is_login = False
        else:
            self.logger.info("处于登录状态...")
            self.is_login = True
        await self.page.close()

    async def auto_login(self):
        super().auto_login()
        await self.page.goto(self.login_url, options={'timeout': 60000})
        try:
            # 知乎使用账号密码登录也会触发反爬机制，用App扫码登录先吧...
            # await asyncio.sleep(2)
            # password_login = await self.page.Jx("//div[text()='密码登录']")
            # await password_login[0].click()
            # input_account = await self.page.Jx("//input[@name='username']")
            # await input_account[0].type(self.account)
            # input_password = await self.page.Jx("//input[@name='password']")
            # await input_password[0].type(self.password)
            # input_login = await self.page.Jx("//button[text()='登录']")
            # await input_login[0].click()
            # await asyncio.sleep(2)
            # # 可能会有验证，等待登录按钮小时
            # await self.page.waitForXPath("//button[text()='登录']", {'hidden': True, 'timeout': 60000})
            # self.logger.info("用户验证成功...")
            qr_code = await self.page.Jx("//div[@aria-label='二维码图片']")
            await qr_code[0].click()
            self.logger.info("等待用户扫码...")
            await self.page.waitForXPath("//span[text()='社交帐号登录']", {'hidden': True, 'timeout': 60000})
            self.logger.info("用户验证成功...")
            self.is_login = True
        except errors.TimeoutError:
            self.logger.info("用户验证失败...")
            self.logger.error("登录超时，请重试...")
            self.is_login = False
        except Exception as e:
            self.logger.error(e)
            self.is_login = False
        finally:
            await self.page.close()

    async def load_write_page(self):
        super().load_write_page()
        await self.page.goto(self.write_page_url, options={'timeout': 60000})
        i_know = await self.page.Jx("//button[text()='我知道了']")
        if i_know is not None and len(i_know) > 0:
            await i_know[0].click()
        await self.fill_content()

    async def fill_content(self):
        super().fill_content()
        # 设置标题
        input_title = await self.page.Jx("//textarea")
        await input_title[0].click()
        await cp_utils.hot_key(self.page, "Control", "KeyA")
        await self.page.keyboard.press("Backspace")
        await asyncio.sleep(1)
        await input_title[0].type(self.article.title)
        await asyncio.sleep(1)

        # 文档导入
        import_document = await self.page.Jx("//button[@aria-label='文档导入']")
        await import_document[0].click()
        sub_import_document = await self.page.Jx("//button[@aria-label='文档导入']")
        await sub_import_document[1].click()
        upload_cover = await self.page.Jx("//input[@type='file' and contains(@accept, 'md')]")
        await upload_cover[0].uploadFile(self.article.md_file)
        await asyncio.sleep(2)
        await self.fill_else()

    async def fill_else(self):
        super().fill_else()
        # 点击发布设置
        publish_setting = await self.page.Jx("//div[text()='发布设置']/parent::button")
        await publish_setting[0].click()
        await asyncio.sleep(1)

        # 添加封面
        upload_cover = await self.page.Jx("//input[@type='file' and @class='UploadPicture-input']")
        await upload_cover[0].uploadFile(self.article.cover_file)
        await asyncio.sleep(1)

        # 添加文章话题，先清空默认选中，再选中
        default_tags = await self.page.Jx("//div[text()='发布设置']/following-sibling::div/div/div/div/button")
        for tag in default_tags:
            await tag.click()
        await asyncio.sleep(1)
        for tag in self.article.tags[:1]:
            add_conversation = await self.page.Jx("//button[text()='添加话题']")
            if add_conversation is not None and len(add_conversation) > 0:
                await add_conversation[0].click()
            search_conversation = await self.page.Jx("//input[@aria-label='搜索话题']")
            if search_conversation is not None and len(search_conversation) > 0:
                await search_conversation[0].type(tag)
                await asyncio.sleep(1)
            tag_button = await self.page.Jx("//button[text()='{}']".format(tag))
            if tag_button is not None and len(tag_button) > 0:
                await tag_button[0].click()
        await asyncio.sleep(1)
        await self.publish_article()

    async def publish_article(self):
        super().publish_article()
        # 发布文章
        publish_article = await self.page.Jx("//button[text()='发布']")
        await publish_article[0].click()
        await asyncio.sleep(2)
        await self.deal_result()

    async def deal_result(self):
        super().deal_result()
        try:
            await self.page.waitForXPath("//span[text()='内容审核中']", {'visible': 'visible', 'timeout': 3000})
            article_url = self.page.url
            if article_url is not None:
                self.logger.info("文章发布成功╰(*°▽°*)╯，链接：{}".format(article_url))
            else:
                self.logger.info("文章发布失败 o(╥﹏╥)o")
        except errors.TimeoutError:
            if self.write_page_url in self.page.url:
                self.logger.info("未知原因发布失败 o(╥﹏╥)o")
        except Exception as e:
            self.logger.info("文章发布失败 o(╥﹏╥)o")
            self.logger.error(e)
        finally:
            await self.page.close()
