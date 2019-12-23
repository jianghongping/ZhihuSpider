import zhihu
from util.conf import Config

Config.init()
Config.CONF.setting('running/style', 0)
Config.CONF.warehouse(r"C:\Users\Milloy\Desktop\items")
zhihu.start(r'https://zhuanlan.zhihu.com/p/98811911')
