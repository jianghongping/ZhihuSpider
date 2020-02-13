import os


class Paper:
    """
    一张高性能的“纸”，它能够高效地管理写入这张“纸”上的文本，
    """

    def __init__(self):
        self.container = list()

    def write(self, item: str):
        """纸张记录内容，向纸上写内容"""
        if not isinstance(item, str):
            raise TypeError(
                'str type is required, not %s' % item.__class__.__name__
            )
        self.container.append(item)

    def save(self, file: str):
        """保存纸上的内容"""
        try:
            with open(file, 'a+', encoding='utf8') as foo:
                foo.truncate(0)
                for line in self.container:
                    foo.write(line)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(file))
            self.save(file)

    def show(self):
        """展示纸上的内容"""
        print(str(self))

    def clear(self):
        """清空纸上的内容"""
        self.container.clear()

    def __str__(self):
        return ''.join(self.container)
