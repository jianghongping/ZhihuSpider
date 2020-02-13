import argparse
import zhihu.spider
from zhihu.conf import config


def main():

    parser = argparse.ArgumentParser(description='Zhihu Spider')

    parser.add_argument('url', action='store', help='项目地址')
    parser.add_argument('-wh', action='store', default=config.wh(), help='文件保存位置')
    parser.add_argument('-ft', action='store', type=str, default='html', help='输出的文件类型，html或markdown（md）')
    parser.add_argument('-cd', action='store_true', help='保存爬取的原始文件')
    parser.add_argument('-cso', action='store_true', help='输出css文件')
    parser.add_argument('-dg', action='store_true', help='下载图片')
    parser.add_argument('--cover', action='store_true', help='覆盖同名文件')

    parser.add_argument('-v', action='version', version='%(prog)s {}'.format(zhihu.__version__))
    parser.add_argument('-version', action='version', version='%(prog)s {}'.format(zhihu.__version__))

    args = parser.parse_args()
    
    file_type = {'html': 0, 'md': 1, 'markdown': 1}

    config.warehouse(args.wh)
    config.setting('running/file_type', file_type.get(args.ft, 0))
    config.setting('running/cached', args.cd)
    config.setting('running/css_output', args.cso)
    config.setting('running/download_image', args.dg)
    config.setting('running/cover', args.cover)
    zhihu.spider.start(args.url)
