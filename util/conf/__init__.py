import json
import os
import pickle


class Config:
    """程序配置信息"""

    CONFIG_FILE = r'.\util\conf\config.pkl'
    CONF = None

    @classmethod
    def init(cls):
        """初始化全局配置文件"""
        try:
            file = os.path.join(os.getcwd(), Config.CONFIG_FILE)
            assert os.path.exists(file)
        except AssertionError:
            raise AttributeError('Config.init be called by NewConcourse only, please use Config().')
        else:
            if cls.CONF is None:
                cls.CONF = Config(file)
            return cls.CONF

    def __init__(self, file):
        if file.endswith('json'):
            self.config = json.loads(open(file, 'r').read())
        elif file.endswith('pkl'):
            self.config = pickle.loads(open(file, 'rb').read())
        else:
            raise ValueError("The file must be end with json or pkl")
        self.file = file

    def save(self, file=None):
        if file is None:
            file = self.file
        opm, encoding, operate = ('w', 'utf8', json) if file.endswith('json') else (
            'wb', None, pickle)
        with open(file, opm, encoding=encoding) as foo:
            operate.dump(self.config, foo)

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value

    def __delitem__(self, key):
        del self.config[key]

    def __iter__(self):
        return iter(self.config)

    @classmethod
    def _setting(cls, region, key):
        try:
            return region[key]
        except KeyError:
            region[key] = dict()
            return cls._get_setting(region, key)
        except TypeError:
            raise ValueError('%s is a setting value, not region.' % region)

    def setting(self, key, value):
        keys = key.split('/')
        region = self.config
        for key in keys[:-1]:
            region = self._setting(region, key)
        region[keys[-1]] = value

    def default_wh(self):
        try:
            # 配置文件中不包含默认路径能保证其正确性，其必然是"Documents\zhihuSpider"
            bw = self.get_setting('running/default_wh')
            assert bw != ''
            return bw
        except (KeyError, AssertionError):
            self.setting('running/default_wh',
                         os.path.join(os.path.expanduser('~'), r'Documents\zhihuSpider'))
            return self.default_wh()

    def _warehouse(self, path):
        if '~' in path:
            path = os.path.normpath(os.path.join(self.warehouse(), path.strip('~')))
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        except OSError:
            # 输入了不合法的路径，不作处理，切回默认路径
            self._warehouse(self.default_wh())
            return
        self.setting('running/warehouse', path)

    def warehouse(self, path=None):
        if path is None:
            try:
                return self.get_setting('running/warehouse')
            except KeyError:
                return self.default_wh()
        self._warehouse(path)
        # 设置完了返回给调用的地方
        return self.warehouse()

    @classmethod
    def _get_setting(cls, region, key):
        return region[key]

    def get_setting(self, key: str):
        region = self.config
        keys = key.split('/')
        try:
            for key in keys:
                region = self._get_setting(region, key)
            return region
        except KeyError:
            raise KeyError('There is no setting option named %s.' % key)

    wh = warehouse
