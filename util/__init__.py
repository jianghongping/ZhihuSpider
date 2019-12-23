class Paper:
    """
    创建一张高性能的“纸”，它能够高效地管理写入这张“纸”上的文本，
    可以将str放入一个list中，写入文件时逐个写进文件
    """

    def __init__(self):
        self.container = list()

    def record(self, item: str):
        if not isinstance(item, str):
            raise TypeError('str type is required, not %s' % item.__class__.__name__)
        self.container.append(item)

    def save(self, file: str):
        with open(file, 'a+', encoding='utf8') as foo:
            foo.truncate(0)
            for line in self.container:
                foo.write(line)

    def show(self):
        print(str(self))

    def clear(self):
        self.container.clear()

    def __str__(self):
        return ''.join(self.container)


class Meta:
    __slots__ = ('author', 'author_avatar_url', 'author_page', 'title', 'original_url',
                 'created_date', 'voteup', 'background')

    def __init__(self, author: str = None, author_avatar_url: str = None, author_page: str = None,
                 title: str = None, original_url: str = None, created_date: str = None,
                 voteup: int = None,
                 background: str = None):
        self.author = author
        self.author_avatar_url = author_avatar_url
        self.author_page = author_page
        self.title = title
        self.original_url = original_url
        self.created_date = created_date
        self.voteup = voteup
        self.background = background
