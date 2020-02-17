# zhihuSpider

程序提供一种简单快捷的方式本地化收藏知乎上的内容以供学习研究。由用户提供知乎上**回答**、**问题**、**文章**、**专栏**等项目的url，爬取一定数量的数据，数据经程序处理后最终输出为**markdown**或**html**文件。项目的侧重点在内容的展示而非内容的爬取，不支持大规模爬取。

第三方依赖库

```python
requests
pygments
```

## 更新

1. 支持 **问题、回答、专栏、文章、用户回答及文章、收藏夹** 的爬取。

2. 重构markdown模块，spider模块，conf模块。

3. 安装后**支持命令行运行**。

## 使用

在命令行不提供任何参数默认输出帮助信息, 等同于`zhihu -h`：
```powershell
>>>zhihu
usage: zhihu [-h] [-u U] [-r R] [-w W] [-f F] [-cd] [-cso] [-dg] [--cover]
             [-v] [-version]

Zhihu Spider

optional arguments:
  -h, --help  show this help message and exit
  -u U        项目url，多个用"$"分割
  -r R        url文本文件，换行分割
  -w W        文件保存位置
  -f F        文件输出类型(html/markdown)
  -cd         缓存原始数据
  -cso        输出css文件
  -dg         下载图片
  --cover     覆盖同名文件
  -v          show program's version number and exit
  -version    show program's version number and exit
```

获取“如何看待2020年非洲蝗虫灾害？”（20190215热榜问题）前40个回答：
```powershell
>>>zhihu -u https://www.zhihu.com/question/371430700
```