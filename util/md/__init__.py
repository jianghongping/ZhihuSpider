import os
import re

from bs4.element import NavigableString as HtmlStr
from bs4.element import Tag as HtmlTag

from util import Meta

REFERENCE_LIST = []
FIGURE_LIST = list()


class Simple:
    """
    设计理念：to_markdown() 完成元素的解析和编译功能，
    直接返回编译结果，不做保存（目前还不需要），仅保留以下函数
    """
    type = 'Simple'
    support = dict()

    def __init__(self, element_tag: HtmlTag = None):
        self.next_sibling = None
        self.element_tag = element_tag

    def to_markdown(self):
        """解析并返回 Tag 的 Markdown 形式"""
        return ''

    def element_type(self):
        """返回类的类型或者None"""
        return self.type

    def detail_type(self):
        """如果元素有细分的具体类型，就返回具体的类型，没有就返回类的类型"""
        return self.type

    def compile_for_quote(self):
        return ''

    def __str__(self):
        return self.type + ': ' + str(self.element_tag)


class Code(Simple):
    type = 'code'
    tag_class = 'highlight'
    support = {'code', 'pre', 'div'}

    def __init__(self, element_tag: HtmlTag = None):
        super().__init__(element_tag)
        self.language = 'text'
        if self.element_tag.name == 'div':
            code = self.element_tag.pre.prettify()
        else:
            code = self.element_tag.prettify()
        search_language = re.search(r'"language-([^()]+)">', code)
        if search_language:
            self.language = re.sub(r'\d+', '', search_language.group(1))
        try:
            regs = (r'(</span>)|(<span class=".+?">)',
                    r'(<pre><code class=".+?">)|(</code></pre>)',
                    r'&lt;', r'&amp;', r'&gt;')
            words = ('', '', '<', '&', '>')
            for reg, word in zip(regs, words):
                code = re.sub(reg, word, code)
            self.code = code
        except AttributeError:
            from util import timer
            file = timer.timestamp() + '.html'
            with open(file, 'w', encoding='utf8') as foo:
                foo.write(self.element_tag.prettify())
            raise ParseError("can't find any code! %s" % file, '')

    def to_markdown(self):
        return '```{}\n{}\n```'.format(self.language, self.code.strip())

    def compile_for_quote(self):
        md = self.to_markdown()
        codes = re.split(r'\n', md)
        code = ''
        for c in codes:
            code += '> ' + c + '\n'
        return code


class Figure(Simple):
    type = 'figure'

    def __init__(self, element_tag: HtmlTag = None):
        super().__init__(element_tag)
        img_attrs = self.element_tag.find('img').attrs
        img_selector = ['data-original', 'data-actualsrc', 'data-default-watermark-src', 'src']
        for img in img_selector:
            self.figure_link = img_attrs.get(img, None)
            if self.figure_link is not None:
                break
        describe_tag = self.element_tag.find('figcaption')
        self.describe = ''
        if describe_tag is not None:
            self.describe = describe_tag.get_text(strip=True)

    def to_markdown(self):
        FIGURE_LIST.append(self.figure_link)
        return '![%s](%s "%s")' % (self.describe, self.figure_link, self.describe)


class Link(Simple):
    type = 'link'
    support = {'a': 'a', 'sup': 'sup'}

    def __init__(self, element_tag: HtmlTag = None):
        super().__init__(element_tag)
        if self.support.get(self.element_tag.name, '') != 'a':
            self.text = self.element_tag['data-text'].strip()
            self.url = self.element_tag['data-url'].strip()
        else:
            try:
                url = self.element_tag['href']
                if not bool(re.search(r'(http)|(www)', url)):
                    url = 'https://www.zhihu.com' + url
                self.url = url
                text = self.element_tag.get_text('#', strip=True)
                self.text = re.sub(r'#.#', '——', text)
            except KeyError as e:
                if self.element_tag.get('data-draft-type', None) == "mcn-link-card":
                    self.text = ''
                    self.url = ''
                else:
                    raise ParseError(element_tag, e.__class__.__name__)

    def to_markdown(self):
        if self.text != '' and self.url != '':
            return ' [%s](%s) ' % (self.text, self.url)
        else:
            return ''


class Url(Simple):
    type = 'a'


class Video(Simple):
    type = 'video'
    tag_class = 'video-box'
    not_video = 'not video type'

    def __init__(self, element_tag: HtmlTag):
        super().__init__(element_tag)
        self.video_link = self.element_tag.find('span', class_='url').get_text(strip=True)
        self.figure_link = self.element_tag.find('img', 'thumbnail')['src']
        title = self.element_tag.find('span', class_='title').get_text(strip=True)
        if title == '':
            title = '无题 '
        describe = '《%s》' % title
        self.video_title = describe

    def to_markdown(self):
        figure = '![%s](%s "%s")' % (self.video_title, self.figure_link, self.video_title)
        video_tip = '**%s，观看视频请访问** ：[%s](%s)' % (
            self.video_title, self.video_link, self.video_link)
        return figure + '\n' + video_tip


class Math(Simple):
    type = 'img'
    type_i = 'inline'
    type_b = 'block'

    def __init__(self, element_tag: HtmlTag):
        super().__init__(element_tag)
        self.img_url = self.element_tag['src'].strip()
        self.expression = self.element_tag['alt']

    def to_markdown(self, style=type_i):
        if style == self.type_i:
            return '$%s$' % self.expression
        else:
            return '$$\n%s\n$$' % self.expression

    def compile_for_quote(self, style=type_i):
        if style == Math.type_i:
            return '> $%s$' % self.expression
        else:
            return '> $$\n> %s\n> $$' % self.expression


class String(Simple):
    type = 'string'
    blank_type = 'ztext-empty-paragraph'
    not_empty = 'not empty'

    def __init__(self, element_tag: (HtmlStr, HtmlTag)):
        super().__init__(element_tag)
        self.text = self.element_tag.strip()

    def to_markdown(self):
        return self.text

    def detail_type(self):
        return super().detail_type()


class NewLine(Simple):
    type = 'br'

    def __init__(self, element_tag: HtmlTag):
        super().__init__(element_tag)
        self.text = '  \n'

    def to_markdown(self):
        return self.text


class Horizontal(Simple):
    type = 'hr'

    def __init__(self, element_tag: HtmlTag):
        super().__init__(element_tag)
        self.text = '---'

    def to_markdown(self):
        return self.text


class Unsupported(Simple):
    type = 'unsupported'

    def __init__(self, element_tag: HtmlTag):
        super().__init__(element_tag)
        self.text = '**不支持的标签：%s**' % self.element_tag.name

    def to_markdown(self):
        return self.text


class Superscript(Simple):
    type = 'sup'

    def __init__(self, element_tag: HtmlTag = None):
        super().__init__(element_tag)
        tag_attrs = self.element_tag.attrs
        self.text = self.element_tag.text.strip()
        self.url = tag_attrs['data-url']
        self.index = tag_attrs['data-numero']
        self.ref_text = tag_attrs['data-text']
        REFERENCE_LIST.append(self)

    def to_markdown(self):
        return '[%s](%s)' % (self.text, self.url)

    def to_reference(self):
        return self.index + '. ' + '[%s](%s)' % (self.ref_text, self.url)


class Multilevel(Simple):
    """
    实现理念：创建对象时解析，to_markdown() 时编译，
    免去了各种编译状态问题，也简化了实现逻辑
    就目前的功能实现还用不到多次 to_markdown() 的情景，
    编译结果直接返回给调用位置，不做保存
    """
    type = 'multilevel'
    support: dict = {}
    blank = ' '

    def __init__(self, element_tag: HtmlTag):
        super().__init__(element_tag)
        self.root = None
        self.probe = None
        head = Simple()
        probe = head
        for element in element_tag.children:
            if isinstance(element, HtmlStr):
                if len(element.strip()) != 0:
                    probe.next_sibling = String(element)
                    probe = probe.next_sibling
                continue
            element_tag_type = element.name
            # br 标签出现的频率特别高，放在第一位有利于提高程序效率
            if element_tag_type == NewLine.type:
                probe.next_sibling = NewLine(element)
            elif element_tag_type in Paragraph.support:
                if element.attrs.get('class', String.not_empty)[0] == String.blank_type:
                    continue
                else:
                    probe.next_sibling = Paragraph(element)
            elif element_tag_type in FontStyle.support:
                probe.next_sibling = FontStyle(element)
            elif element_tag_type == Url.type:
                try:
                    element_class = element.attrs.get('class', Video.not_video)[0]
                    probe.next_sibling = Video(
                        element) if element_class == Video.tag_class else Link(element)
                except IndexError:
                    probe.next_sibling = Link(element)
            elif element_tag_type in Table.support:
                probe.next_sibling = Table(element)
            elif element_tag_type in Code.support:
                if element_tag_type == 'div':
                    try:
                        element_class = element.attrs.get('class')[0]
                    except TypeError:
                        print(element_tag.prettify())
                    probe.next_sibling = Code(
                        element) if element_class == Code.tag_class else Paragraph(element)
                else:
                    probe.next_sibling = Code(element)
            else:
                probe.next_sibling = tag_dict.get(element_tag_type, Unsupported)(element)
            probe = probe.next_sibling
        self.root = head.next_sibling

    def to_markdown(self):
        """创建对象时解析，to_markdown() 时编译"""
        return super().to_markdown()

    def detail_type(self):
        return super().detail_type()

    @staticmethod
    def add_blank(element: Simple):
        """判断编译时是否需要在兄弟标签的编译内容首尾添加空格"""

        if element.next_sibling is not None:
            return element.detail_type() in [Link.type, *FontStyle.format_type,
                                             Unsupported.type, Superscript.type]
        else:
            return False

    def __len__(self):
        probe = self.root
        length = 0
        while probe is not None:
            length += 1
            probe = probe.next_sibling
        return length

    def __iter__(self):
        self.probe = self.root
        return self

    def __next__(self):
        try:
            item = self.probe
            self.probe = self.probe.next_sibling
            return item
        except AttributeError:
            raise StopIteration


class Text(Multilevel):
    type = 'text'

    def __init__(self, element_tag: HtmlTag):
        super().__init__(element_tag)

    def to_markdown(self):
        text = ''
        for paragraph in self:
            if isinstance(paragraph, Math):
                para = paragraph.to_markdown(Math.type_b)
            else:
                para = paragraph.to_markdown()
            if para != '':
                text += para + '\n\n'
        ref_text = ''
        if len(REFERENCE_LIST) != 0:
            ref_text = '**参考资料**：\n\n'
            for ref in REFERENCE_LIST:
                ref_text += ref.to_reference() + '\n'
        return text + ref_text


class Paragraph(Multilevel):
    type = 'paragraph'
    support: dict = {'p': 'p', 'span': 'span'}

    def __init__(self, element_tag: HtmlTag):
        super().__init__(element_tag)
        # if '模2运算中两个相同的数相加为' in self.element_tag.prettify():
        #     print('__init__:', self.element_tag)

    def to_markdown(self):
        paragraph = ''
        for sentence in self:
            if isinstance(sentence, Math) and len(self) == 1:
                sent = ' {} '.format(sentence.to_markdown(Math.type_b))
            else:
                sent = sentence.to_markdown()
                if self.add_blank(sentence):
                    sent = ' {} '.format(sent)
            paragraph += sent
        return paragraph

    def compile_for_quote(self):
        if len(self) == 1 and isinstance(self.root, Math):
            return self.root.compile_for_quote(style=Math.type_b)
        else:
            return self.to_markdown()


class Quote(Multilevel):
    type = 'blockquote'
    support = {'blockquote'}

    def __init__(self, element_tag: HtmlTag):
        super().__init__(element_tag)

    def to_markdown(self):
        sentences = list()
        sentence = ''
        for quote in self:
            if isinstance(quote, NewLine):
                if sentence != '':
                    sentences.append('> ' + sentence + '  \n')
                    sentence = ''
            elif isinstance(quote, Paragraph):
                if sentence != '':
                    sentences.append('> ' + sentence + '  \n')
                sentences.append('> ' + quote.to_markdown() + '  \n')
                sentence = ''
            elif isinstance(quote, Code) or isinstance(quote, Table) or isinstance(quote, Math):
                if sentence != '':
                    sentences.append('> ' + sentence + '  \n')
                sentences.append(quote.compile_for_quote())
                sentence = ''
            else:
                q = quote.to_markdown()
                if self.add_blank(quote):
                    q += ' '
                sentence += q
        if sentence != '':
            sentences.append('> ' + sentence + '  \n')
        return ''.join(sentences)


class Table(Multilevel):
    type = 'table'
    type_ul = 'ul'
    type_ol = 'ol'
    support = {'ul': 'ul', 'ol': 'ol'}

    def __init__(self, element_tag: HtmlTag):
        super().__init__(element_tag)
        self.index = 0

    def to_markdown(self):
        table_md = ''
        for li in self:
            li_md = li.to_markdown()
            table_md += self.get_index() + li_md.strip() + '\n'
        return table_md

    def get_index(self):
        if self.support.get(self.element_tag.name, '') == 'ol':
            self.index += 1
            return str(self.index) + '. '
        return '- '

    def compile_for_quote(self):
        table_md = ''
        for li in self:
            li_md = li.to_markdown()
            table_md += '> ' + self.get_index() + li_md.strip() + '  \n'
        return table_md


class FontStyle(Multilevel):
    type = 'font_style'
    support: dict = {'h1': 'h1', 'h2': 'h2', 'h3': 'h3', 'h4': 'h4', 'h5': 'h5', 'h6': 'h6',
                     'em': 'em', 'strong': 'strong', 'b': 'b', 'i': 'i', 'u': 'u', 'li': 'li'}
    plus_type = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'u', 'li'}
    plus_span = {'h1': '# ', 'h2': '## ', 'h3': '### ', 'h4': '#### ', 'h5': '##### ',
                 'h6': '###### ',
                 'u': '', 'li': ''}
    format_type = {'em', 'strong', 'b', 'i'}
    format_span = {'em': '**{}**', 'strong': '**{}**', 'b': '**{}**', 'i': '*{}*'}

    def __init__(self, element_tag: HtmlTag):
        super().__init__(element_tag)

    def to_markdown(self):
        paragraph = ''
        for sentence in self:
            sent = sentence.to_markdown()
            if self.add_blank(sentence):
                sent += ' {} '.format(sent)
            paragraph += sent
        if self.detail_type() in self.plus_type:
            md = self.plus_span.get(self.detail_type(), '') + paragraph
        else:
            md = self.format_span.get(self.detail_type(), '{}').format(paragraph)
        return md

    def detail_type(self):
        return self.support.get(self.element_tag.name, '')


class ParseError(Exception):
    def __init__(self, tag: HtmlTag, error_type):
        self.tag = tag
        self._error_type = error_type
        if isinstance(tag, HtmlTag):
            tag = tag.prettify()
        et = 'ParseError: {}'.format(error_type)
        txt = "\n{}\n{}\n{}".format(tag, '=' * len(et), et)
        super(ParseError, self).__init__(txt)

    def __reduce__(self):
        return self.__class__, (self.tag, self.error_type)

    @property
    def error_type(self):
        return self._error_type

    @error_type.setter
    def error_type(self, error_type):
        self._error_type = error_type


class Markdown:
    def __init__(self, tag, meta: Meta):
        self.author = meta.author
        self.author_avatar_url = meta.author_avatar_url
        self.author_page = meta.author_page
        self.title = meta.title
        self.original_url = meta.original_url
        self.created_date = meta.created_date
        self.voteup = meta.voteup
        self.background = meta.background
        self.file_name = ''
        self.text = Text(tag)
        self.markdown = self.compile()

    def get_file_name(self, template):
        """%v-%d-%a-%t"""
        title = re.sub(r'[\\/]', '、', self.title)
        title = re.sub(r'[？?*:<>"|\n\t]', '', title)
        date = re.sub(r'-', '', self.created_date)
        file_name_split = {'%a': self.author, '%d': date, '%t': title, '%v': str(self.voteup)}
        file_name_t = template.split('-')
        names = []
        for te in file_name_t:
            e = file_name_split.get(te, '')
            names.append(e)
        name = '-'.join(names)
        return name + '.md'

    def make_markdown(self, file):
        try:
            with open(file, 'w', encoding='utf-8') as foo:
                foo.write(self.markdown)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(file))
            self.make_markdown(file)

    def compile(self):
        background = ''
        if self.background is not None and self.background != '':
            background = '![背景大图](%s)\n\n' % self.background
        title = '# [%s](%s)\n\n' % (self.title, self.original_url)
        split_line = '-' * len(title) + '\n\n'
        head_img = '![%s](%s "%s")&emsp;' % (self.author, self.author_avatar_url, self.author)
        author = '**[%s](%s) / %s**\n\n' % (
            self.author, self.author_page, self.created_date)
        markdown_head = background + title + split_line + head_img + author
        return markdown_head + self.text.to_markdown()

    def to_markdown(self):
        return self.markdown

    def __iter__(self):
        return iter(self.text)

    def set_file_name(self, template=None, file_name=None):
        if template is not None:
            self.file_name = self.get_file_name(template)
        elif file_name is not None:
            self.file_name = file_name
        else:
            raise ValueError

    def __str__(self):
        return '%s\n%s / %s' % (self.title, self.author, self.created_date)


def save_images(file):
    try:
        with open(file, 'w', encoding='utf8') as foo:
            foo.write('\n'.join(FIGURE_LIST))
    except FileNotFoundError:
        try:
            os.makedirs(os.path.dirname(file))
            with open(file, 'w', encoding='utf8') as foo:
                foo.write('\n'.join(FIGURE_LIST))
        except OSError:
            pass


# 这个字典应用于 Multilevel 中的构造函数，不宜随意修改！
tag_dict = {Quote.type: Quote, Figure.type: Figure, Math.type: Math,
            NewLine.type: NewLine, Horizontal.type: Horizontal, Superscript.type: Superscript}
