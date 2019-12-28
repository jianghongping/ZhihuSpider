import zhihu
from util.conf import Config

Config.init()
Config.CONF.setting('running/style', 0)
Config.CONF.setting('running/saving', True)
zhihu.start(r'https://zhuanlan.zhihu.com/p/98811911')
