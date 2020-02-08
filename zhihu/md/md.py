from zhihu import Meta


class Markdown:
    def __init__(self, content, meta: Meta):
        self.meta = meta


class Compile:
    def __init__(self, tags):
        self.tags = tags

    def compile(self):
        self._compile(self.tags)

    def _compile(self, tags):
        for tag in tags:
            # TODO Compile tag
            self._compile(tag.contents)
