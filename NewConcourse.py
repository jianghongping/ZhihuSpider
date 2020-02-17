import zhihu.spider
from zhihu.conf import config

config.warehouse(r'C:\Users\Milloy\Desktop')
config.setting('running/file_type', 0)
config.setting('running/cached', False)
config.setting('running/css_output', False)
config.setting('running/download_image', False)
config.setting('running/cover', False)
zhihu.spider.start(r'https://www.zhihu.com/question/311008958/answer/592584375')

# gif pic https://www.zhihu.com/question/59392068/answer/541759976
# pics https://www.zhihu.com/question/311008958/answer/592584375

