import zhihu.spider
from zhihu.conf import Config

Config.init()
Config.CONF.warehouse(r'C:\Users\Milloy\Desktop')
Config.CONF.setting('running/style', 0)
Config.CONF.setting('running/saving', False)
Config.CONF.setting('running/link_css', False)
zhihu.spider.start(r'https://www.zhihu.com/question/356227923/answer/935252726')
