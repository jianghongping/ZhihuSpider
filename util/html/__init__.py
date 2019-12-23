import os
import re


class Paper:
    """
    一张高性能的“纸”，它能够高效地管理写入这张“纸”上的文本，
    """

    def __init__(self):
        self.container = list()

    def record(self, item: str):
        """纸张记录内容，向纸上写内容"""
        if not isinstance(item, str):
            raise TypeError('str type is required, not %s' % item.__class__.__name__)
        self.container.append(item)

    def save(self, file: str):
        """保存纸上的内容"""
        try:
            with open(file, 'a+', encoding='utf8') as foo:
                foo.truncate(0)
                for line in self.container:
                    foo.write(line)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(file))
            self.save(file)

    def show(self):
        """展示纸上的内容"""
        print(str(self))

    def clear(self):
        """清空纸上的内容"""
        self.container.clear()

    def __str__(self):
        return ''.join(self.container)


class Tag:
    """
    html标签的抽象：
    <div class="box"><p>我们都是<strong>好孩子</strong></p></div>

    观察上面的div标签，发现它由三部分构成：
        start:    起始标签，含属性
        end:      尾标签
        contents: 内容，起止标签包围的内容，字符串或其他标签

    进一步观察发现p和strong标签也是由上述三部分构成，只是它们倆没有属性。
    为了统一化，把字符串也抽象成为一个没有名字和属性的特殊标签。
    """
    SELF_CLOSING = ['img', 'link', 'br', 'hr', 'meta']

    def __init__(self, name, attrs: dict = None, contents: list = None, string: str = None,
                 indent: bool = True):
        """
        :param name: 标签名称，如div
        :param attrs: 标签属性
        :param contents: 标签内容，一般通过.add()添加
        :param string: 字符串，用于创建名字为None的字符串标签，或者普通标签的字符串content
        :param indent: .write（）时是否缩进，默认True，主要用于<code><pre>
        """
        # 如果标签的内容只有一个string，可以在创建标签时传入string，这样做是没有问题的。
        # 但如果标签含有标签内容，同时传入string，string会被添加到content的末尾，可能会导致次序混乱。
        # 所以建议标签只含有string时传入string
        self.name = name
        self.attrs = dict() if attrs is None else attrs
        self.contents = list()
        if contents is not None:
            self.add(*contents)
        if name is None:
            self._string = string
        elif string is not None:
            self.add(Tag(None, string=string, indent=indent))
        self.to_indent = indent

    def write_down(self, paper, indent=0):
        padding = ' ' * 4 * indent if self.to_indent else ''
        if self.name is None:
            paper.record('%s%s\n' % (padding, self.string))
            return
        attrs = self._str_attrs() if len(self.attrs) != 0 else ''
        paper.record('%s<%s%s>\n' % (padding, self.name, attrs))
        for c in self.contents:
            c.write_down(paper, indent + 1)
        if self.name not in self.SELF_CLOSING:
            paper.record('%s</%s>\n' % (padding, self.name))

    def add(self, *items):
        # 在Compile过程中由于Compile.a()的需要，
        # 它返回的是None，这里做一个对象检测也是可以的
        for item in items:
            if isinstance(item, Tag):
                self.contents.append(item)
            elif item is not None:
                raise TypeError(
                    'Tag type is needed, but %s type is given.' % item.__class__.__name__)

    @property
    def string(self):
        return self.get_text(split='')

    def get_text(self, split='', strip=True):
        """返回self包含地所有文本，用split分隔不同标签之间的文本
        :param strip: True
        :type split: str
        """
        """这里有一个隐含的递归算法，能得到所有contents的string，不论嵌套多少层"""
        if self.name is None:
            return self._string
        else:
            s = list()
            for c in self.contents:
                s.append(c.string.strip() if strip else c.string)
            return split.join(s)

    def find_tag(self, name, limit, **kwargs):
        found_list = list()
        if self.name == name and self._attrs_match(kwargs):
            found_list.append(self)
        else:
            for tag in self.contents:
                if len(found_list) == limit:
                    return found_list
                found_list.extend(tag.find_tag(name, limit, **kwargs))
        return found_list

    def _find(self, name, limit, attrs, **kwargs):
        try:
            attrs.updata(kwargs)
        except AttributeError:
            attrs = kwargs
        if '_class' in attrs.keys():
            attrs['class'] = attrs['_class']
            del attrs['_class']
        found_list = self.find_tag(name, limit, **attrs)
        if len(found_list) == 0:
            return None
        return found_list[0] if limit == 1 else found_list

    def find(self, name, attrs=None, **kwargs):
        return self._find(name, limit=1, attrs=attrs, **kwargs)

    def find_all(self, name, attrs=None, **kwargs):
        return self._find(name, limit=-1, attrs=attrs, **kwargs)

    def not_empty(self):
        return True if self.name in ('br', 'hr') else not (
                len(self.contents) == 0 and self.string == '')

    def get_attrs(self, item, default=None):
        try:
            return self[item]
        except AttributeError:
            return default

    def _attrs_match(self, attrs):
        """多值匹配法检查属性值是否匹配（包含）"""
        for attr, value in attrs.items():
            attr_val = self.attrs.get(attr, None)
            try:
                attr_vas = re.split('\s+', attr_val)
                vas = re.split('\s+', value) if isinstance(value, str) else value
                for v in vas:
                    if v not in attr_vas:
                        return False
            except AttributeError:
                return False
        return True

    def _str_attrs(self):
        s = list()
        for key, value in self.attrs.items():
            s.append('%s="%s"' % (key, value))
        return ' ' + ' '.join(s)

    def __str__(self):
        p = Paper()
        self.write_down(p)
        return str(p)

    def __len__(self):
        return len(self.contents)

    def __getitem__(self, key):
        try:
            return self.attrs[key]
        except KeyError:
            raise AttributeError('%s tag no attribute named %s' % (self.name, key))


class Bowl:
    def __init__(self, bgg=None, hed=None, tex=None, div=None):
        self.bgg = bgg
        self.hed = hed
        self.tex = tex
        self.div = div

    def clear(self):
        self.__init__()

    def is_empty(self):
        judge = 0
        for val in self.__dict__.values():
            if val is not None:
                judge += 1
        return judge == 0

    def __iter__(self):
        ls = (self.bgg, self.hed, self.tex)
        for i in ls:
            if i is not None:
                yield i

    def setattr(self, key, value):
        self.__setattr__(key, value)

    def __setattr__(self, key, value):
        if key in ('bgg', 'tex', 'hed', 'div'):
            self.__dict__[key] = value
        else:
            raise AttributeError('Bowl class not have "%s" attribute.' % key)


class Mushroom(Tag):

    def __init__(self, title, config):
        super().__init__('html', attrs={'lang': 'zh'})
        self._head = Tag('head')
        self._head.contents.append(Tag('title', string=title))
        self.title = title
        for tag in config.get_setting('head/essential').values():
            self.add_tag_to_head(tag)
        # 为body添加<div id=write>标签，现在不能使用self.add()添加
        self._body = Tag('body')
        self.contents.append(self._head)
        self.contents.append(self._body)
        self.cur_art = None
        self.bwl = Bowl()
        self.new_article(divide=False)
        self._parsing = Parsing()
        self.words = 0
        self.media = 0
        self._config = config

    def add_tag_to_head(self, tag):
        """添加用字典表示的标签到HTML的head标签"""
        self._head.contents.append(
            Tag(tag['name'], attrs=tag.get('attrs', {}),
                string=tag.get('string', None))
        )

    def add_optional_style(self, style_meta):
        """动态添加css样式"""
        # 比如包含代码内容的HTML就需要添加代码样式的css，而不包含代内容的就不需要，因而动态。
        try:
            for style in style_meta:
                self.add_tag_to_head(self._config.get_setting('head/optional/%s' % style))
        except KeyError:
            pass

    def new_article(self, divide=True):
        """
        html: new_article() 新建一篇文章，并添加到 body content，
        添加新文章必须使用这个方法，构造HTML时会默认创建一篇

        新建文章时会检查self.bwl 是否为空，如果不是就先将它“清空”再创建新文章
        """
        self._merge()
        if divide:
            self.bwl.div = Tag('div', attrs={'class': 'divide'})
        self.cur_art = Tag('div', attrs={'class': 'article'})

    def _merge(self):
        if not self.bwl.is_empty():
            self.cur_art.add(self.bwl.bgg, self.bwl.hed, self.bwl.tex)
        self._body.add(self.bwl.div, self.cur_art)
        self.bwl.clear()

    def write_down(self, paper, indent=0):
        self._merge()
        paper.record('<!DOCTYPE html>\n')
        super().write_down(paper)

    def add(self, *items):
        if self.bwl.tex is None:
            self.bwl.tex = Tag('div', attrs={'class': 'text'})
        self.bwl.tex.add(*items)

    def add_to_article(self, name, tag):
        try:
            self.bwl.setattr(name, tag)
        except AttributeError:
            raise ValueError('object %s is not expect.' % name)


class TagGenerate:
    """依据模板和数据生成html标签"""

    @classmethod
    def generate_tag_by_template(cls, template, marks_value=None, **kwargs):
        try:
            marks_value.update(kwargs)
        except AttributeError:
            marks_value = kwargs
        return Parsing().parse_tmp(template, marks_value)[0]

    def __init__(self, config):
        self._config = config
        self.parsing = Parsing()

    def template(self, name):
        try:
            return self._config.get_setting('tag/%s' % name)
        except KeyError:
            raise KeyError('not find template named %s.' % name)

    @classmethod
    def generate_tag_by_describe(cls, top_tag_name, contents_name, contents_attrs, contents_str,
                                 **kwargs):
        """以top_tag为顶层标签描述性地生成html标签"""
        # 不好描述
        # 没有需求
        # 缺乏灵活性
        pass

    def _generate_tag_by_template(self, template, marks_value=None, **kwargs):
        try:
            marks_value.update(kwargs)
        except AttributeError:
            marks_value = kwargs
        return self.parsing.parse_tmp(template, marks_value)[0]

    def link_card(self, url, title, img=None):
        try:
            domain = re.search('target=https?%3A//([^/]+)', url).group(1)
        except AttributeError:
            domain = re.search('https?://([^/]+)', url).group(1)
        mas_val = {
            'domain': domain,
            'link-card-image': img if img is not None else '',
            'link-card-url': url,
            'link-card-title': title
        }
        name = 'lc_img' if img is not None else 'lc_svg'
        return self._generate_tag_by_template(self.template(name), marks_value=mas_val)

    def article_header(self, original_article_link, user_avatar, user_name, user_link, created_date,
                       title):
        mas_val = {'article-origin': original_article_link,
                   'user-avatar': user_avatar,
                   'user-name': user_name,
                   'user-link': user_link,
                   'created-date': created_date,
                   'title': title
                   }
        return self._generate_tag_by_template(self.template('header'), marks_value=mas_val)

    def article_figure(self, img_link):
        mas_val = {'background-image': img_link}
        return self._generate_tag_by_template(self.template('bgg'), marks_value=mas_val)

    def video_box(self, video_link, cover_link, tip=None):
        # TODO 针对有无视频标题做两套video box
        mas_val = {'video-link': video_link,
                   'video-cover': cover_link,
                   'video-tip': '点击封面可观看视频!' if tip is None else '%s，%s' % (tip, '点击封面可观看视频!')
                   }
        return self._generate_tag_by_template(self.template('video'), marks_value=mas_val)

    def reference_index(self, index):
        return self._generate_tag_by_template(self.template('ref_ind'), {'index': str(index)})

    def reference(self, index, ref_title, ref_url):
        mas_val = {
            'index': str(index),
            'ref-url': ref_url,
            'ref-title': ref_title
        }
        return self._generate_tag_by_template(self.template('quo'), mas_val)

    def reference_table(self, ref_title_url):
        table = Tag('table', attrs={'class': 'reference'})
        index = 1
        for title, url in ref_title_url:
            table.add(
                self.reference(
                    index=index,
                    ref_title=title if title != '' else url,
                    ref_url=url)
            )
            index += 1
        return table


def wrapper_handle_attrs(func):
    """转化html的标签属性为字典"""

    # 这是一个装饰Parsing.handle_attrs_tmp、Parsing.handle_attrs_tag的装饰器
    def handle_attrs(self, attrs_str):
        if attrs_str == '/':
            return dict()
        attrs = dict()
        attrs_list = re.findall(self.attr_reg, attrs_str)
        for attr in attrs_list:
            attrs[attr[0]] = func(self, attr)
        return attrs

    return handle_attrs


def except_handle_string(func):
    """处理字符串"""

    # 捕获stg != '' 的断言装饰器
    def handle_string(self, stg):
        try:
            return func(self, stg)
        except AssertionError:
            pass

    return handle_string


class Parsing:
    """解析HTML生成Tag，返回由Tags组成的contents_list"""
    # #########实现原理#########
    # <div class="header">
    #     <div class="title">
    #         <a href="__ar-or__" target="_blank">文章标题</a>
    #     </div>
    #     <a class="UserLink-link" target="_blank" href="__us-li__">
    #         <div class="AuthorInfo">
    #             <div class="Popover">
    #                 <img class="Avatar" width="50" height="50" src="__us-av__" alt="__us-na__"/>
    #             </div>
    #             <div class="AuthorInfo-content">
    #                 <div class="AuthorInfo-name"><span>用户名</span></div>
    #                 <div class="AuthorInfo-detail"><span>发表日期和点赞数量</span></div>
    #             </div>
    #         </div>
    #     </a>
    # </div>
    #
    #     html标签一般由起始标签、尾标签和内容三部分共同构成，起止标签包围的内容都归它所有，被它“接收”。
    # 同样，它包含的子标签也需要“接收”自身的内容，直到出现尾标签。因此需要一个栈来暂时存放标签，往后的内容
    # 都归处于栈顶的标签“接收”，直到尾标签出现，栈顶出栈，栈顶的后继元素成为新栈顶继续“接收”它的内容。
    #     创建一个栈（stack），从左向右扫描html，一旦发现是起始标签（start）就创建这个标签(Tag)，并让它
    # 入栈（append）“接收”内容（content），继续向下扫描，如果发现新的标签就add到栈顶contents，同时让它入栈，
    # 如果是字符串，它必定被栈顶标签包围，直接add到栈顶contents。每扫描到一个尾标签，就让栈顶出栈（pop）。
    #     这种解析方式要求html标签必须拥有完整起止标签，缺失起止标签都将导致内容“接收”出现混乱（结构混乱），
    # 过多或过少接收。没有起始标签，它的尾标签将导致栈顶标签提前弹出；缺失尾标签，其将滞后甚至不弹出栈顶。

    # Questions：
    # 如何处理传入的是并列标签的情况？
    # 它可能有contents，先入栈，出栈时append到contents_list
    # 每发现一个尾标签栈顶就出栈，起止标签两两成对，所以不存在并列标签滞留在stack中导致出错的情况

    # append内容到stack时有两种情况：直接append或先add到栈顶contents再append到stack
    # 前者，说明它是一个父级标签，将与前后标签构成兄弟关系（并列标签），出栈后要append到contents_list；
    # 后者，说明它只是一个content（子级标签），入栈是为了“接收”它的contents，出栈后不需要append到contents_list.
    # 所以要对两种情况进行区分，方法是入栈时添加一个状态码：
    # 前者，状态码为 1
    # 后者，状态码为 0

    # 如何匹配代码？
    # 观察到<pre>或<code>标签就使用正则表达式做最小闭合匹配，把匹配内容当成字符串（string）
    # 针对知乎Spider可能观察到<div class="highlight">就对<pre>做闭合匹配比较好
    # 如果匹配到<pre>或<code>，ofs回退r.end()，用code_reg匹配，作为字符串add到栈顶contents或append到contents_list（栈空）
    # 也可以将<pre>或<code>做成标签(Tag)，它的content就是去除起止标签后剩余的元素，ofs要减去len('</%s>' % Tag.name)
    # 如果匹配到<div class="highlight">，构造div标签，然后用code_reg匹配，作为字符串add到div,然后将整个div，add或append
    # 需要特殊处理ofs

    # 匹配起始标签和属性
    start = re.compile('<(\w+)([^<>]*?)(/?)>')

    # 从start的匹配结果中匹配属性和属性值（re.findall()）
    attr_reg = re.compile("""(\w+)\s*=\s*["']([^<>"']*)["']""")

    # 匹配字符串
    string = re.compile('([^<>]+)|(<!DOCTYPE html>)')

    # 匹配尾标签
    end = re.compile('</(\w+)>')

    # 匹配注释
    comment = re.compile(r'<!--[\s\S]*?-->')

    # 匹配code或pre标签内的代码，包括给代码添加样式的span标签
    code_reg = re.compile('(<code[^<>]*?>[\s\S]+?</code>)|(<pre[^<>]*?>[\s\S]*?</pre>)')

    # 匹配标识符的名称，关于标识符见marks.py
    mark = re.compile(r'__([a-zA-Z0-9\-]+)__')  # 下划线 _ 属于 \w，在这里不能用

    SELF_CLOSING = ['img', 'link', 'br', 'hr', 'meta']

    def __init__(self):
        self._ofs = 0
        self._marks_value = dict()
        self._contents_list = list()
        self._stack = list()
        self._tag = ''

    def restore(self):
        """还原Parsing到初始状态"""
        self.__init__()

    def arouse_error(self, max_loop):
        """检查解析过程是否正常，不正常将引发ValueError"""
        if max_loop != 0:
            return
        w = 'While loop go beyond the max_loop(%d). ' \
            'The following words is showed below line.' % len(self._tag)
        raise ValueError('%s\n%s\n\n%s' % (w, '-' * (len(w) + 12), self._tag[self._ofs:]))

    def replace(self, stg):
        """处理html模板中的字符串并替换标识符的值"""
        mark = re.search(self.mark, stg)
        while mark:
            value = self._marks_value.get(mark.group(1), '##')
            stg = re.sub(self.mark, value, stg, 1)
            mark = re.search(self.mark, stg)
        return stg

    def parse_tag(self, tag):
        """解析html标签生成Tag并返回由Tags构成的列表"""
        self._tag = tag
        return self.parsing(funcs=(self.handle_start_tag, self.handle_string_tag,
                                   self.handle_end, self.handle_comment))

    def parse_tmp(self, tmp, marks_val):
        """解析html模板生成Tag，并在解析过程中将模板上的占位符替换成marks_val提供的对应值"""
        self._tag = tmp
        self._marks_value = marks_val
        return self.parsing(funcs=(self.handle_start_tmp, self.handle_string_tmp,
                                   self.handle_end, self.handle_comment))

    def parsing(self, funcs):
        """解析html标签"""
        regs = (self.start, self.string, self.end, self.comment)
        max_loop = len(self._tag)
        # 可以预见html的标签（元素）数量不可能等于或超过它本身的字符数量
        # 设定max_loop可以避免遇到无法匹配的情况时，进度停滞不前，程序陷入死循环
        while self._ofs < len(self._tag) and max_loop > 0:
            max_loop -= 1
            for reg, func in zip(regs, funcs):
                # 循环匹配tag文本直到匹配成功并调用相关的处理方法func
                r = re.match(reg, self._tag[self._ofs:])
                if bool(r):
                    self._ofs += r.end()
                    func(r)
                    break
        # 检查htm是否解析完全，如果没有，将引起错误
        self.arouse_error(max_loop)
        # 这个类有点像加工厂，来料加工，加工完之后要还原到原来的状态，等料加工
        ct = self._contents_list
        self.restore()
        return ct

    def handle_start_tag(self, r):
        """处理起始标签"""
        self.handle_start(r, make_attrs=self.handle_attrs_val_tag)

    def handle_start_tmp(self, r):
        """处理起始标签（模板）"""
        self.handle_start(r, self.handle_attrs_val_tmp)

    def handle_string_tag(self, r):
        """处理html中的字符串"""
        self.handle_string(r.group().strip())

    def handle_string_tmp(self, r):
        """处理html模板中的字符串并替换标识符的值"""
        self.handle_string(
            self.replace(
                r.group().strip()
            )
        )

    def handle_end(self, r):
        """处理html标签的尾标签，涉及栈顶元素的弹出"""
        n, status_code = self._stack.pop()
        # 如果n是顶层父级标签则需要将其加入到内容列表
        if status_code == 1:
            self._contents_list.append(n)

    def handle_comment(self, r):
        """html中的注释，不处理"""
        pass

    def handle_code(self, n, r):
        """处理代码标签"""
        if n.name == 'div' and n.attrs.get('class', None) == 'highlight':
            cd = re.match(self.code_reg, self._tag[self._ofs:])
            if bool(cd):
                self._ofs += cd.end()
                n.add(Tag(None, string=cd.group(), indent=False))
        elif n.name in ('code', 'pre'):
            cof = self._ofs - r.end()
            cd = re.match(self.code_reg, self._tag[cof:])
            if bool(cd):
                self._ofs = cof + cd.end() - len('</%s>' % n.name)
                stg = re.sub('</?%s[^<>]*?>' % n.name, '', cd.group())
                n.add(Tag(None, string=stg, indent=False))

    def handle_start(self, r, make_attrs):
        """处理起始标签"""
        if r.group(1) in self.SELF_CLOSING:
            n = Tag(r.group(1),
                    attrs=make_attrs(r.group(2) if len(r.groups()) != 1 else '/'))
            # 可以确定它没有contents，直接append到content_list或add到stack
            if len(self._stack) == 0:
                self._contents_list.append(n)
            else:
                self._stack[-1][0].add(n)
        else:
            n = Tag(r.group(1), attrs=make_attrs(r.group(2)))
            self.handle_code(n, r)
            # 如果栈为空，直接append到栈顶，
            # 否则就是栈顶有元素，n是栈顶的content，
            # 先add到栈顶contents再append到栈顶，成为新的栈顶
            if len(self._stack) == 0:
                self._stack.append((n, 1))
            else:
                self._stack[-1][0].add(n)
                self._stack.append((n, 0))

    @except_handle_string
    def handle_string(self, stg):
        """根据传入的字符串构造Tag，并将其添加到（栈顶）内容列表"""
        assert stg != ''
        n = Tag(None, string=stg)
        if len(self._stack) == 0:
            self._contents_list.append(n)
        else:
            self._stack[-1][0].add(n)

    @wrapper_handle_attrs
    def handle_attrs_val_tmp(self, attrs_val):
        """"转化html的标签属性为字典，并替换标识符的值"""
        return self.replace(attrs_val[1])

    @wrapper_handle_attrs
    def handle_attrs_val_tag(self, attrs_val):
        """"转化html的标签属性为字典"""
        return attrs_val[1].strip()


class Compile:
    FIGURE_LIST = list()

    def __init__(self, contents_list: list, tag_generate):
        self._cl = contents_list
        self._parsing = Parsing()
        self.tag_generate = tag_generate
        self._ref_list = list()
        self._ref_ind = 1
        self._style_meta = set()

    @property
    def style_meta(self):
        return self._style_meta

    def compile(self):
        """处理Tags，修改属性、生成视频标签等"""
        r = self._compile(self._cl)
        if len(self._ref_list) != 0:
            r.append(Tag('span', attrs={'style': 'font-size:24px'}, string='参考资料'))
            n = self.tag_generate.reference_table(self._ref_list)
            r.append(n)
        return r

    def _compile(self, contents):
        """处理Tags"""
        contents_list = list()
        for tag in contents:
            if tag.name in ('a', 'div', 'figure', 'img', 'sup'):
                # 使用Tag的名字作为索引，利用self.__getattribute__()
                # 获取对应的处理方法self.a, self.div, self.figure
                # len(contents)用来计算Tag的contents个数，供self.img判断
                # 这是行间公式还是行内公式
                contents_list.append(
                    self.__getattribute__(tag.name)(tag, len(contents)))
                continue
            tag.contents = self._compile(tag.contents)
            self._remove_attrs(tag)
            if tag.not_empty():
                contents_list.append(tag)
        return contents_list

    def figure(self, tag, sibling):
        """处理figure标签，图片"""
        img = tag.find('img', _class='lazy')
        try:
            url = img['original']
        except AttributeError:
            url = img['actualsrc']
        except TypeError:
            # 没找着，返回了None
            pass
        if not re.match(r'^https?', img['src']):
            url = re.sub(r'\.[a-z]+$', '.gif', url)
        return Tag('figure', contents=[Tag('img', attrs={'src': url}), tag.find('figcaption')])

    def img_(self, tag, sibling):
        """处理数学公式"""
        self._style_meta.add('script1')
        self._style_meta.add('script2')
        # TODO 本地渲染数学公式很慢而且有些公式不支持，考虑使用知乎原版公式
        name, code = (None, '$${}$$') if sibling == 1 else ('span', '\({}\)')
        return Tag(name, string=code.format(tag['alt']))

    def img(self, tag, sibling):
        """处理数学公式"""
        return tag

    def div(self, tag, sibling):
        """处理div标签，代码"""
        self._style_meta.add('styleCode')
        return tag

    def a(self, tag, sibling):
        """处理a标签，视频、卡片链接、广告、普通链接"""
        if tag.find('a', **{'class': 'video-box'}) is not None:
            return self._make_video_box(tag)
        elif tag.find('a', **{'type': 'link-card'}) is not None:
            return self._make_link_card(tag)
        elif tag.find('a', **{'tag': 'block'}) is not None:
            # 广告，tag自动过滤None
            return None
        else:
            return tag

    def sup(self, tag, sibling):
        """处理sup标签，知乎标准的文献引用样式"""
        self._ref_list.append((tag['text'], tag['url']))
        self._ref_ind += 1
        return self.tag_generate.reference_index(self._ref_ind - 1)

    def _make_video_box(self, tag):
        """生成视频标签"""
        return self.tag_generate.video_box(
            video_link=tag.find('span', _class='url').string,
            cover_link=tag.find('img')['src'],
            tip=tag.find('span', **{'class': 'title'}).string
        )

    def _make_link_card(self, tag):
        """生成卡片链接标签"""
        url = tag.get_attrs('href')
        img = tag.get_attrs('image')
        if re.search('zhihu', url) and img is None:
            img = 'https://zhstatic.zhihu.com/assets/zhihu/editor/zhihu-card-default.svg'
        return self.tag_generate.link_card(
            url=url,
            title=tag.string,
            img=img
        )

    @staticmethod
    def _remove_attrs(tag):
        """移除标签的属性"""
        tag.attrs = dict()
        return tag


if __name__ == '__main__':
    b = Bowl()
    b.bgg = 'https'
    b.setattr('bgg', 'gg')
    print('b.bgg', b.bgg)
    b.setattr('value', 'value')
