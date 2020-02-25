# zhihuSpider

程序提供一种简单快捷的方式**本地化收藏**知乎上的内容，如：**答案**、**文章**等，并尽可能保持内容格式与知乎上的一致。由用户提供知乎上相应项目的url，通过知乎API爬取数据数据，数据经解析后最终输出为**markdown**或**html**文件存储到本地，同时可下载内容附带的图片。

第三方依赖库

```python
requests
pygments
```

## 更新

1. 支持 **问题、答案、专栏、文章、收藏夹、用户答案及文章** 的爬取。

2. 重构部分代码，增强爬虫的扩展性。

3. 安装后**支持命令行运行**。

## 使用

在命令行不提供任何参数时默认输出帮助信息, 等同于`zhihu -h`：

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

获取“如何看待2020年非洲蝗虫灾害？”（20190215热榜问题） **前2%** 个答案：

```powershell
>>>zhihu -u https://www.zhihu.com/question/371430700
```
