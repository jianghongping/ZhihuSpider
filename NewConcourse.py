import zhihu
from util.conf import Config

Config.init()
Config.CONF.setting('running/style', 0)
Config.CONF.warehouse(r"C:\Users\Milloy\Desktop\items")
zhihu.start(r'https://www.zhihu.com/question/23148377/answer/714596562')
