__all__ = ['multilevel', 'ParseError']
"""
    parse 模块可以说是这个脚本的核心，代码还有很大的重构空间。
"""


class ParseError(ValueError):
    pass


if __name__ == '__main__':
    raise ParseError
