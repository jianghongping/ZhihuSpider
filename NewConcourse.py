import zhihu
from util.conf import Config

Config.init()
Config.CONF.setting('running/style', 0)
Config.CONF.setting('running/saving', False)
Config.CONF.setting('running/link_css', False)
zhihu.start(r'https://zhuanlan.zhihu.com/p/34395749')
