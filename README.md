<p  align="left">
    <a href="https://github.com/coder-pig/"><img alt="logo" width="36" height="36" src="res/head_icon.png" alt="coderpig">
    </a>
</p>

<p  align="center">
<img src="res/ic_avatar.png">
</p>

<p align="center" style="margin: 30px 0 35px;"> 🤡 Markdown文章多平台发布工具</p>

**`ChaoMdPublish`** 是一款基于 **`Python`** 实现的，帮助 **`创作者`** 将一篇文章同时发布到多个平台的工具 (**`一文多发`**)。

**缘由与介绍**：[Van♂Python | 焯！🤡随手写个文章多平台发布脚本][1]

**实现原理**：**Pyppeteer自动化模拟** (就是开个浏览器自动点点点~)

**支持平台**：

- [x] [掘金](https://juejin.cn/)
- [x] [CSDN博客](https://blog.csdn.net/)
- [x] [51CTO博客](https://home.51cto.com/index)
- [x] [简书](https://www.jianshu.com/)
- [x] [知乎](https://zhuanlan.zhihu.com)
- [ ] SegmentFault
- [ ] 博客园
- [ ] 开源中国
- [ ] 微博
- [ ] 慕课手记 
- [ ] 今日头条
- [ ] 微信公众号
- [ ] ...欢迎提issues反馈补充~

## 0x1、使用讲解

目前只支持命令行咯，可能用起来不够直观，好像也有点繁琐，后续有闲情会学下Python的图形化库，整个图形化界面简化一波，也可能会学下Chrome插件的开发，写个类似于 [OpenWrite][2] 的插件，先将就着用吧~

### ① 使用前的准备工作

- **Step 1**：通过Git把代码clone到本地，或是直接Download代码压缩包；
- **Step 2**：**安装Python环境**，如何安装请自行百度，安装了的直接跳过；
- **Step 3**：通过**pip命令**安装用到的依赖库；

```
pip install -r requirements.txt
```

### ② 先运行一遍

运行项目中的 **`app.py`** 文件，第一次运行会生成默认所需的相关文件：

![][3]

生成文件在 **`input`** 目录下：

![][4]

### ③ 替换文章相关

按需覆盖内容，另外手下文章配置json，这里进行一些文章附加信息的配置，一般改这些就好：

![][5]

先统一化处理了，平台差异问题，后续会提供单独的配置模板。

### ③ 配置站点账号密码 (只需进行一次)

找到项目中的 **`website_config.json`** 文件，然后填充账号密码：

![][6]

不想发布的站点，可以把 **`is_publish`** 字段设置为 **`false`**

### ④ 再运行一遍

脚本执行流程 (会开始一个浏览器自动执行)：

- ① 校验文章相关；
- ② 检验登录状态，未登录会跳转自动登录，有些平台有验证码啥的，要验证一下~
- ③ 验证完开始自动发布文章；

**Tips**：只需登录一次，登录状态会保存，运行效果图如下 (具体 → [演示视频][7])：

![][8]


因时间有限，工具还算粗糙，笔者目前用着还行，后续会把一些bug修复下，弄个图形用户页面，让其更好更易用，谢谢~


  [1]: https://juejin.cn/post/7032129362056970254
  [2]: https://openwrite.cn/
  [3]: http://static.zybuluo.com/coder-pig/961q098fecie87dt0m7l9kki/fgfhz.png
  [4]: http://static.zybuluo.com/coder-pig/9tjsoy16nem04crzp5mrewhb/gfhh.png
  [5]: http://static.zybuluo.com/coder-pig/7bcopj39x71f8l02ovt831h9/hghgz.png
  [6]: http://static.zybuluo.com/coder-pig/q4im1s5lchooodh4wpmvoivs/hgjfj.png
  [7]: https://www.bilibili.com/video/BV1ZY411x7Cv/
  [8]: http://static.zybuluo.com/coder-pig/k10nymdue58horkiwgmeyqb7/xg2.gif