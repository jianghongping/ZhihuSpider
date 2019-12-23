""""""
"""
标识符
标识符是项目自定义的一种占位符，可以作为HTML的属性值和string值，起到标识或占位作用，主要用在HTML模板中。
标识符由英文字符或数字及分隔符“-”组合构成的名称和两侧各两个的下划线“_”组成。如“__article-url__”。
分隔符“-”在这里起到分隔作用，标识符中的文字（字母、数字）只能使用“-”分隔，不能使用空格或其他字符。
不使用分隔符，如“__articleUrl__”也是合法的。

<div class="header">
    <div class="title">
        <a href="__article-origin__" target="_blank">__title__</a>
    </div>
    <a class="UserLink-link" target="_blank" href="__user-link__">
        <div class="AuthorInfo">
            <div class="Popover">
                <img class="Avatar" width="50" height="50" src="__user-avatar__" alt="头像">
            </div>
            <div class="AuthorInfo-content">
                <div class="AuthorInfo-name"><span>__user-name__</span></div>
                <div class="AuthorInfo-detail"><span>__created-date__</span></div>
            </div>
        </div>
    </a>
</div>

下面是项目中用到的部分标识符
到目前为止，项目中对作者等一系列的命名是不统一的。例如，Meta中将作者命名为author，但这里却是user。

__background-image__: 文章题图链接

 __article-origin__ : 文章或回答原文链接
     __title__      : 文章或回答标题，回答用问题代替
   __user-link__    : 作者个人主页链接
  __user-avatar__   : 作者头像
   __user-name__    : 作者昵称
  __created-date__  : 文章或回答发表时间

   __video-link__   : 文章或回答中的视频链接
  __video-cover__   : 视频封面链接
   __video-tip__    : 视频标题和提示信息

 __link-card-url__  : 卡片式超链接的链接
__link-card-image__ : 卡片式超链接的配图和背景图
__link-card-title__ : 卡片式超链接的题注
     __domain__     : 卡片式超链接链接的主机域名，如：www.zhihu.com

     __index__      : 参考文献引用序号
    __ref-url__     : 参考文献引用url
   __ref-title__    : 参考文献引用标题
"""


if __name__ == '__main__':
    import re

    tag = open(r'commit\element.html', 'r',
               encoding='utf8').read()
    ls = re.findall(r'__[A-Za-z-]+__', tag)
    max_v = 0
    for l in ls:
        max_v = len(l) if len(l) > max_v else max_v

    template = '{:^%d}: ' % max_v
    for l in ls:
        print(template.format(l))
