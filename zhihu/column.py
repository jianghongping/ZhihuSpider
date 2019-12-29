import codecs
import os
import pickle
import re

import util.timer as timer
import zhihu.core as zc
from util import Meta
from util.conf import Config

CRAWLER = zc.Crawler()


class ColumnMange:
    """ColumnManage实际要管理的是id列表，分批多次爬取，每次爬取时更新id列表"""
    config_file = Config.CONF.get_setting('ColumnManage/config_file')

    def __init__(self, column_id):
        self.column_id = column_id
        self.status_config = self.read_working_status()
        self.totals = None
        self.title = None
        # self.totals, self.title将在self.column_totals()中初始化
        self.column_totals()
        mcs = Config.CONF.get_setting('running/mcs')
        self.mcs = mcs if mcs <= self.totals else self.totals
        self.current_count = 0

    @property
    def offset(self):
        try:
            return self.column_status['offset']
        except KeyError:
            self.column_status['offset'] = 0
            return self.offset

    @offset.setter
    def offset(self, num):
        self.column_status['offset'] = num

    @property
    def column_status(self):
        try:
            return self.status_config[self.column_id]
        except KeyError:
            self.status_config[self.column_id] = dict()
            return self.column_status

    @column_status.setter
    def column_status(self, item):
        self.status_config[self.column_id] = item

    @classmethod
    def save_working_status(cls, status_config):
        """保存工作状态"""
        with open(os.path.join(os.getcwd(), cls.config_file), 'wb') as foo:
            pickle.dump(status_config, foo)

    @classmethod
    def read_working_status(cls):
        """读取工作状态"""
        try:
            with open(os.path.join(os.getcwd(), cls.config_file), 'rb') as foo:
                return pickle.loads(foo.read())
        except FileNotFoundError:
            # raise FileNotFoundError('ColumnMange working status file is not found.')
            return dict()

    def update_id_list(self, id_list):
        column_id_status = self.column_status.get('ids', dict())
        for each_id in id_list:
            column_id_status[each_id] = column_id_status.get(each_id, False)
        self.column_status['ids'] = column_id_status
        self.save_working_status(self.status_config)

    def clear_finish(self):
        """判断该专栏上的文章是否完全爬取，如果是，则清除该专栏的全部文章id列表"""
        try:
            finish_count = 0
            for each_id, status in self.column_status.get('ids', dict()).items():
                if status is True:
                    finish_count += 1
            if finish_count == self.totals:
                del self.status_config[self.column_id]
            self.save_working_status(self.status_config)
        except KeyError:
            """del 处引发的错误，此时还没有构建column的文章id列表，属于错误调用本方法"""
            pass

    def get_article(self):
        style = Config.CONF.get_setting('running/style')
        article_ids = self.column_status.get('ids', dict())
        amount = 0
        for each_id, status in article_ids.items():
            if status is False:
                if style == zc.STYLE:
                    finish = article2html(each_id)
                else:
                    finish = article2md(each_id)
                timer.random_sleep(end=zc.SLEEP)
                if finish is True:
                    amount += 1
                    article_ids[each_id] = True
        # TODO OUTPUT TAG
        print('总数：', amount)
        self.clear_finish()

    @zc.catch_error_cls
    def get_article_id(self):
        id_list = list()
        while self.go_on():
            response = CRAWLER.column_spider(self.column_id, self.next_offset())
            ids = re.findall(r'"id":\s*(\d+)', response.text)
            self.increase(len(ids))
            id_list.extend(ids)
            print(self.next_offset(), zc.GET_ARTICLES_ID)
            timer.random_sleep(end=zc.SLEEP)
        self.update_id_list(id_list)

    @zc.catch_error_cls
    def column_totals(self):
        response = CRAWLER.column_msg_spider(self.column_id)
        title = re.search(Config.CONF.get_setting('ColumnManage/title_reg'),
                          response.text).group(1)
        title = codecs.decode(title, 'unicode_escape')
        Config.CONF.warehouse(
            '~column/%s' % zc.format_path(title))
        self.totals = int(re.search(Config.CONF.get_setting('ColumnManage/totals_reg'),
                                    response.text).group(1))
        self.title = title

    def increase(self, num):
        self.current_count += num
        self.offset += num

    def next_offset(self):
        return self.offset

    def go_on(self):
        return self.current_count < self.mcs and self.offset < self.totals

    @classmethod
    def meta(cls, cont):
        meta = Meta()

        meta.original_url = zc.ARTICLE_URL.format(cont['id'])
        meta.voteup = cont['voteup_count']
        meta.title = cont['title']
        meta.background = cont['image_url']
        meta.created_date = timer.timestamp_to_date(cont['created'])
        meta.author = cont['author']['name']
        meta.author_page = zc.AUTHOR_PAGE_URL.format(
            cont['author']['url_token'])
        meta.author_avatar_url = cont['author']['avatar_url']
        return meta

    def summary_info(self):
        """展示工作信息"""
        """
        title:
        number:
        warehouse:
        """
        print(self.title)
        print(self.current_count)
        print(Config.CONF.wh())


def column(column_id):
    col = ColumnMange(column_id)
    col.get_article_id()
    col.get_article()


@zc.catch_error_func
def article2md(article_id):
    response = CRAWLER.article_spider(article_id)
    response_json = response.json()
    zc.item2md_holder(response_json['content'], ColumnMange.meta(response_json))


@zc.catch_error_func
def article2html(article_id):
    response = CRAWLER.article_spider(article_id)
    response_json = response.json()
    zc.item2html_holder(response_json['content'], ColumnMange.meta(response_json))
    return True
