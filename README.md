# zhihuSpider

## 关于项目

项目在开发机器(win 10, python3.7)上测试通过，其他机器自测。

项目的功能是提供一种简单快捷的方式本地化收藏知乎上的内容以供学习研究。由用户提供知乎上回答、问题、文章、专栏的url，爬取一定数量的数据，数据经程序处理后最终输出为markdown或html文件。项目的侧重点在内容的展示而非内容的爬取，不支持大规模爬取。

第三方依赖库

```python
requests
bs4
```

## 更新

1. 仅支持问题、回答、专栏、文章的爬取，其他栏目（如收藏夹）不再支持。同时，增加了爬取量的限制。其中，一个问题最多爬取40个高赞回答（2次网络访问），保存不多于16个；专栏支持多次运行分批爬取，每次运行爬取不超过20篇（共22次网络访问）。

2. 新增html模块，支持将爬取的内容转换成html。相对于markdown而言，html在阅读方面更方便，版面也更美观。原用于解析生成markdown的parse模块改成md模块。

3. 删除net模块，由简单的Crawler类替代net模块，提供网络访问功能。

4. 使用正则表达式匹配url包含的id，并判断id类型，免去人工提取。

5. 新增全局配置模块（Config），程序运行过程用到的全部设置信息、数据都能由Config提供，一次初始化全局有效。

6. 新增图片保存功能，该功能目前还没有开放。

## 关于md模块

将爬取的数据（html标签）利用BeautifulSoup解析，根据html和markdown的语法进行转化，最终输出markdown文本。如果需要打印，推荐转成markdown文件，再用阅读器转换成其他格式，如pdf或doc。

## 关于html模块

网络获取的回答、文章数据原本以html标签的形式组织，由html模块上多个类联合工作，将部分不能直接展示的内容重新组织，最终输出html文本文件。

相对于markdown，html在阅读和版面上都有优势，markdown需要专门的软件打开，而html能直接用浏览器打开阅读；版面上基本保留了知乎的风格，增加了首行缩进两字符，题头参考了某些博客的排版设计，整体上更美观。感官上，转换成html，程序运行速度更快。

### Tag

html标签的抽象，能够保存一个完整的html标签，包括嵌套的标签。

### Parsing

html标签的解析，利用正则表达式解析html标签生成Tag。Parsing和Tag的联合功能有点类似于BeautifulSoup，md模块的重构会考虑使用这两个类替代BeautifulSoup。

## 使用方式

NewConcourse.py是爬虫的入口，在`start()`函数填写需要爬取的url即可，默认保存在`user/文档/zhihuSpider`。

```python
import zhihu
from util.conf import Config

Config.init()
Config.CONF.setting('running/style', 0)
Config.CONF.warehouse(path='')
zhihu.start(url='')
```

1. 初始化全局配置管理器

Config是全局配置管理器，程序运行过程中用到的所有数据、设置信息都可以由它提供。

```python
Congfig.init()
```

2. 设置信息

目前通过`Config.CONF`调用全局配置管理器，设置信息通过`Config.CONF.setting(key, value)`设置。

目前可设置的信息：

- 输出类型，默认`html`：

```python
key = 'running/style'
value = 0    # 0表示输出html，非0表示输出markdown
Config.CONF.setting(key, value)
```

- 保存目录，默认`文档\zhihuSpider`：

```python
key='running/warehouse'
value=path    # 任意合法可读写的目录
Config.CONF.setting(key, value)
```

关于warehouse有以下两种快捷方法：

```python
Config.CONF.warehouse(path)
Config.CONF.wh(path)
```

在path前加`~`表示保存在主目录的path子目录下，仅限调用上述两种快捷方法时使用，不合法的path会引起哪些错误暂时不知。

1和2都不是必须的，程序启动后内部会检查有无配置管理器，没有则自动初始化一个，但设置信息必须手动初始化配置管理器。

3. 输入链接或id

新版本使用正表达式自动匹配id并判断id的类型（answer, question, article, column)。

```python
zhihu.start(url)
```

如果确实需要使用id，使用`zhihu.start_with_id(item_id, item_type)`启动。

## 版权

项目仅供学习交流，请尊重知乎用户版权，不要随意爬取、传播内容。因使用本项目造成的纠纷与本人无关。不要用于商业、非法用途。
