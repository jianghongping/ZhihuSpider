import zhihu.spider
from zhihu.conf import Config

Config.init()
Config.CONF.warehouse(r'C:\Users\Milloy\Desktop')
Config.CONF.setting('running/file_type', 0)
Config.CONF.setting('running/cached', False)
Config.CONF.setting('running/stylesheet_inline', True)
Config.CONF.setting('running/download_image', True)
zhihu.spider.start(r'https://www.zhihu.com/question/346306748/answer/829732537')
