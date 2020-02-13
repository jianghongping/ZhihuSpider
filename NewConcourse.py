import zhihu.spider
from zhihu.conf import config

config.warehouse(r'C:\Users\Milloy\Desktop')
config.setting('running/file_type', 1)
config.setting('running/cached', False)
config.setting('running/css_output', False)
config.setting('running/download_image', False)
config.setting('running/cover', False)
zhihu.spider.start(r'https://www.zhihu.com/question/371351587/answer/1012291312')

