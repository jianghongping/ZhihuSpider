import os
import re

import requests
from bs4 import BeautifulSoup
from requests import HTTPError

import zhihu.html as uh
import zhihu.md as umd
from zhihu import timer
from zhihu.conf import Config

Config.init()
GET_ARTICLES_ID = Config.CONF.get_setting('core/GET_ARTICLES_ID')
SLEEP = Config.CONF.get_setting('core/SLEEP')
SORT_BY_VOT = Config.CONF.get_setting('core/SORT_BY_VOT')

# 作者头像
AVATAR_SIZE_R = Config.CONF.get_setting('core/AVATAR_SIZE_R')
AVATAR_SIZE_A = Config.CONF.get_setting('core/AVATAR_SIZE_A')  # This is L.
# size: r, m, b, l, xs, is, s

# 作者主页 format: url_token
AUTHOR_PAGE_URL = Config.CONF.get_setting('core/AUTHOR_PAGE_URL')

# 答案原文链接 format: question_id, answer_id
ANSWER_URL = Config.CONF.get_setting('core/ANSWER_URL')

# 文章原文链接 format: article_id
ARTICLE_URL = Config.CONF.get_setting('core/ARTICLE_URL')

STYLE = Config.CONF.get_setting('core/STYLE')  # 0表示生成html，非0表示生成markdown


class VerityError(ValueError):
    """网络数据验证异常"""

    def __init__(self, *args):
        super(VerityError, self).__init__(*args)


class API:
    """获得有关数据的链接类"""

    LIMIT_size = Config.CONF.get_setting('API/LIMIT_size')
    ANSWER_API = Config.CONF.get_setting('API/ANSWER_API')
    CC_ARTICLE_API = Config.CONF.get_setting('API/CC_ARTICLE_API')
    A_AS_API = Config.CONF.get_setting('API/A_AS_API')
    CC_MSG_API = Config.CONF.get_setting('API/CC_MSG_API')
    QS_MSG_API = Config.CONF.get_setting('API/QS_MSG_API')
    ARTICLE_API = Config.CONF.get_setting('API/ARTICLE_API')

    @staticmethod
    def article_api(article_id: str) -> str:
        return API.ARTICLE_API.format(article_id)

    @staticmethod
    def answer_api(answer_id: str) -> str:
        return API.ANSWER_API.format(answer_id)

    @staticmethod
    def columns_article_api(column_id: str, offset: int, limit: int) -> str:
        return API.CC_ARTICLE_API.format(column_id, limit, offset)

    @staticmethod
    def all_answers_api(question_id: str, limit: int, offset: int, sort_by: str) -> str:
        return API.A_AS_API.format(question_id, limit, offset, sort_by)

    @staticmethod
    def columns_msg_api(column_id: str) -> str:
        return API.CC_MSG_API.format(column_id)

    @staticmethod
    def question_msg_api(question_id: str) -> str:
        return API.QS_MSG_API.format(question_id)


def verity(func):
    """验证网络请求结果"""
    def verity_deco(self, *args, **kwargs):
        """验证返回的网络数据是否正确，确保输入到核心库数据的正确性"""
        # 验证不通过就引发VerityError
        rs = None
        try:
            rs = func(self, *args, **kwargs)
            rs.raise_for_status()
        except HTTPError:
            raise VerityError('%s: 网络错误！' % rs.status_code)
        return rs

    return verity_deco


def cached(func):
    """保存json数据"""
    def cached_func(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if Config.CONF.get_setting('running/saving') is True:
            itd = kwargs.get('item_id', args[0])
            try:
                ofs = kwargs.get('offset', args[1])
            except IndexError:
                ofs = timer.timestamp_str()
            file = os.path.join(Config.CONF.cached_warehouse(), '%s-%s.json' % (itd, ofs))
            with open(file, 'w', encoding='utf8') as foo:
                foo.write(res.text)
        return res

    return cached_func


class Crawler(requests.Session):

    UA = Config.CONF.get_setting('Crawler/user-agent')

    def __init__(self):
        super().__init__()
        self.headers.update(Crawler.UA)

    @verity
    def pull_response(self, url):
        r = self.get(url, timeout=10)
        r.encoding = 'utf8'
        return r

    @cached
    def article_spider(self, item_id):
        return self.pull_response(API.article_api(item_id))

    @cached
    def column_spider(self, item_id, offset):
        return self.pull_response(API.columns_article_api(item_id, offset, 20))

    @cached
    def answer_spider(self, item_id):
        return self.pull_response(API.answer_api(item_id))

    @cached
    def question_spider(self, item_id, offset):
        return self.pull_response(API.all_answers_api(item_id, 20, offset, SORT_BY_VOT))

    @cached
    def column_msg_spider(self, item_id):
        return self.pull_response(API.columns_msg_api(item_id))

    @cached
    def question_msg_spider(self, item_id):
        return self.pull_response(API.question_msg_api(item_id))


def catch_error_cls(func):
    """捕获VerityError并处理，装饰类方法"""

    def catch(self):
        try:
            return func(self)
        except VerityError:
            handle_error()
            return False

    return catch


def catch_error_func(func):
    """捕获VerityError并处理，装饰普通函数"""

    def catch(item_id):
        try:
            return func(item_id)
        except VerityError:
            handle_error()
            return False

    return catch


def handle_error():
    """网络返回错误数据时应做的处理"""
    print('网络错误，未返回正确数据！')


def format_path(path):
    """替换文件路径中的非法字符"""
    return re.sub(r'[\\/:*?"<>|]', '#', path)


def file_name(suffix, *part_name):
    """返回正确的文件名"""
    names = format_path('-'.join(part_name))
    file = os.path.join(Config.CONF.wh(), '%s.%s' % (names, suffix))

    if Config.CONF.get_setting('running/cover'):
        return file

    REPETITION = 1
    while os.path.exists(file):
        file = os.path.join(
            Config.CONF.wh(),
            '%s-%d.%s' % (names, REPETITION, suffix)
        )
        REPETITION += 1
    return file


def item2html_holder(cont, meta):
    p = uh.Compile(cont).compile(meta, uh.Mushroom(meta.title)).write_down(uh.Paper())
    p.save(file_name('html', meta.author, meta.title))
    show_info(meta)


def item2md_holder(cont, meta):
    an = umd.Markdown(BeautifulSoup(cont, 'lxml').body, meta)
    file = file_name('md', meta.author, meta.title)
    an.make_markdown(file)
    show_info(meta)


def show_info(meta):
    print('%5d\t%s\t《%s》' % (meta.voteup, meta.author, meta.title))
