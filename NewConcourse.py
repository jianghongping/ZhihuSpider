import zhihu.spider
from zhihu.conf import config

config.warehouse(r'C:\Users\Milloy\Desktop')
config.setting('running/file_type', 0)
config.setting('running/cached', False)
config.setting('running/css_output', False)
config.setting('running/download_image', False)
config.setting('running/cover', False)
zhihu.spider.start(r'https://www.zhihu.com/question/25699277')

