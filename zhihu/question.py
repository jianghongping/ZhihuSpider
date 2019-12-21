import codecs
import os
import re
from json.decoder import JSONDecodeError

import util.timer as timer
import zhihu.core as zc
from util import Meta
from util.conf import Config


class QuestionMange:
    _least_words = 256
    _least_img = 8
    _max_amount = 16
    BATCH_SIZE = 2

    def __init__(self, question_id):
        self.question_id = question_id
        self.title = self.warehouse()
        self.offset = 0
        self.totals = 1
        self.batch_size = 0
        self.response_list = list()

    @classmethod
    def parse_response(cls, *responses):
        """解析response为json数据"""
        data = list()
        for response in responses:
            try:
                data.extend(response.json()['data'])
            except (JSONDecodeError, KeyError):
                pass
        return data

    def assess_content(self, cont):
        return (len(re.findall(Config.CONF.get_setting('QuestionManage/Chinese_reg'),
                               cont)) > self._least_words
                or len(re.findall(Config.CONF.get_setting('QuestionManage/img_reg'),
                                  cont)) > self._least_img)

    @zc.catch_error_cls
    def get_response(self):
        while self.go_on():
            response = CRAWLER.question_spider(self.question_id, self.next_offset())
            rjs = response.json()
            self.response_list.extend(rjs['data'])
            if self.totals == 1:
                self.totals = rjs['paging']['totals']
            self.increase(len(rjs['data']))
            timer.random_sleep(end=zc.SLEEP)
        self.batch_size = 0

    def get_answer(self, selective=True):
        style = Config.CONF.get_setting('running/style')
        if selective is True:
            self.response_list = sorted(self.response_list, key=lambda x: x['voteup_count'],
                                        reverse=True)
        amount = 1
        for each_ans in self.response_list:
            cont, meta = self.content(each_ans), self.meta(each_ans)
            if selective and (self.assess_content(cont) is False):
                continue
            if style == zc.STYLE:
                zc.item2html_holder(cont, meta)
            else:
                zc.item2md_holder(cont, meta)
            if selective and (amount == self._max_amount):
                # TODO OUTPUT TAG
                print(amount)
                break
            amount += 1
        self.response_list.clear()

    def get_img(self):
        images = set()

        for each_ans in self.response_list:
            cont = self.content(each_ans)
            igs = re.findall(Config.CONF.get_setting('QuestionManage/img_reg'), cont)
            images.update(igs)

        self.response_list.clear()
        file = os.path.join(Config.CONF.wh(), 'images.text')
        with open(file, 'w', encoding='utf8') as foo:
            foo.write('\n'.join(images))
        print('size: %s\t%s' % (len(images), file))
        return images

    def go_on(self):
        return self.batch_size < self.BATCH_SIZE and self.offset < self.totals

    def next_offset(self):
        return self.offset

    def increase(self, num):
        self.batch_size += 1
        self.offset += num

    @zc.catch_error_cls
    def warehouse(self):
        response = CRAWLER.question_msg_spider(self.question_id)
        title = re.search(Config.CONF.get_setting('QuestionManage/title_reg'),
                          response.text).group(1)
        title = codecs.decode(title, 'unicode_escape')
        Config.CONF.warehouse(
            '~question/%s' % zc.format_path(title))
        return title

    @classmethod
    def content(cls, cont):
        try:
            return cont['content']
        except KeyError:
            print(cont)
            raise KeyError

    @classmethod
    def meta(cls, cont):
        meta = Meta()
        meta.author = cont['author']['name']
        meta.voteup = cont['voteup_count']
        meta.title = cont['question']['title']
        question_id = cont['question']['id']
        answer_id = cont['id']
        meta.original_url = zc.ANSWER_URL.format(question_id, answer_id)
        meta.author_page = zc.AUTHOR_PAGE_URL.format(
            cont['author']['url_token'])
        meta.author_avatar_url = \
            cont['author']['avatar_url_template'].replace(
                zc.AVATAR_SIZE_R, zc.AVATAR_SIZE_A)
        meta.created_date = timer.timestamp_to_date(cont['created_time'])
        return meta

    def crawling(self):
        """配合while结构可以实现爬取所有回答，这里不提供！"""
        return self.totals > self.offset

    def summary_info(self):
        """展示工作信息"""
        """
        title:
        number:
        warehouse:
        """
        print(self.title)
        print(self.offset)
        print(Config.CONF.wh())


CRAWLER = zc.Crawler()


def question(question_id):
    qm = QuestionMange(question_id)
    qm.get_response()
    qm.get_answer()


def question_img(question_id):
    qm = QuestionMange(question_id)
    qm.get_response()
    return qm.get_img()


@zc.catch_error_func
def answer2md(answer_id):
    response = CRAWLER.answer_spider(answer_id)
    if response is not None:
        answer_content = response.json()
        meta = QuestionMange.meta(answer_content)
        zc.item2md_holder(answer_content['content'], meta)
    else:
        raise ValueError('Response is None')


@zc.catch_error_func
def answer2html(answer_id):
    response = CRAWLER.answer_spider(answer_id)
    if response is not None:
        item = response.json()
        zc.item2html_holder(
            QuestionMange.content(item), QuestionMange.meta(item)
        )
    else:
        raise ValueError('Response is None')


if __name__ == '__main__':
	pass