""""""
"""
标识符
标识符是项目自定义的一种占位符，可以作为HTML的属性值和string值，起到标识或占位作用，主要用在HTML模板中。
标识符由英文字符或数字及分隔符“-”组合构成的名称和两侧各两个的下划线“_”组成。如“#__#article-url##__”。
分隔符“-”在这里起到分隔作用，标识符中的文字（字母、数字）只能使用“-”分隔，不能使用空格或其他字符。
不使用分隔符，如“#__#articleUrl##__”也是合法的。

<div class="header">
    <div class="title">
        <a href="__article-origin#__" target="_blank">__title#__</a>
    </div>
    <a class="UserLink-link" target="_blank" href="__user-link#__">
        <div class="AuthorInfo">
            <div class="Popover">
                <img class="Avatar" width="50" height="50" src="__user-avatar#__" alt="头像">
            </div>
            <div class="AuthorInfo-content">
                <div class="AuthorInfo-name"><span>__user-name#__</span></div>
                <div class="AuthorInfo-detail"><span>__created-date#__</span></div>
            </div>
        </div>
    </a>
</div>

下面是项目中用到的部分标识符
到目前为止，项目中对作者等一系列的命名是不统一的。例如，Meta中将作者命名为author，但这里却是user。

__#background-image#__: 文章题图链接

 __#article-origin#__ : 文章或回答原文链接
     __#title#__      : 文章或回答标题，回答用问题代替
   __#user-link#__    : 作者个人主页链接
  __#user-avatar#__   : 作者头像
   __#user-name#__    : 作者昵称
  __#created-date#__  : 文章或回答发表时间

   __#video-link#__   : 文章或回答中的视频链接
  __#video-cover#__   : 视频封面链接
   __#video-tip#__    : 视频标题和提示信息

 __#link-card-url#__  : 卡片式超链接的链接 __#link-card-image#__ : 卡片式超链接的配图和背景图 __#link-card-title#__ : 卡片式超链接的题注
     __#domain#__     : 卡片式超链接链接的主机域名，如：www.zhihu.com

     __#index#__      : 参考文献引用序号
    __#ref-url#__     : 参考文献引用url
   __#ref-title#__    : 参考文献引用标题
"""

if __name__ == '__main__':
    import re

    tag = open(r'commit\element.html', 'r',
               encoding='utf8').read()
    ls = re.findall(r'__#[A-Za-z-]+#__', tag)
    max_v = 0
    for l in ls:
        max_v = len(l) if len(l) > max_v else max_v

    template = '{:^%d}: ' % max_v
    for l in ls:
        print(template.format(l))
