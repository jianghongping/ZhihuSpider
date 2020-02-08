from zhihu.spider.column import *
from zhihu.spider.core import get_item_with_id
from zhihu.spider.question import *


def start_with_id(item_id, item_type):
    if item_type == 'article':
        get_item_with_id(item_id, html_func=article2html, md_func=article2md)
    elif item_type == 'answer':
        get_item_with_id(item_id, html_func=answer2html, md_func=answer2md)
    elif item_type == 'column':
        column(item_id)
    elif item_type == 'question':
        question(item_id)
    # TODO OUTPUT TAG
    print('保存目录：%s' % Config.CONF.wh())


def start(item_link):
    Config.init()
    item_id, item_type = get_id(item_link)
    start_with_id(item_id, item_type)


def get_id(item_link):
    for reg, ty in zip(
            ('^https?.+?zhuanlan.zhihu.com/([\w\d]+)$',
             '^https?.+?zhuanlan.zhihu.com/p/(\d+)$',
             '^https?.+?question/(\d+)$',
             '^https?.+?answer/(\d+)$'),

            ('column', 'article', 'question', 'answer')
    ):
        r = re.search(reg, item_link)
        if bool(r):
            return r.group(1), ty
    raise ValueError('can not find the item id.')
