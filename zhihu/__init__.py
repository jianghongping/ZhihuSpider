__version__ = 5.0


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
