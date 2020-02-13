from setuptools import setup, find_packages

import zhihu

setup(
    name='Zhihu Spider',
    version=zhihu.__version__,
    keyword=('zhihu', 'spider'),
    packages=find_packages(),
    url='https://github.com/Milloyy/ZhihuSpider',
    license='MIT',
    author='小鬼',
    author_email='',
    description='本地化收藏知乎优质内容，包括特定答案，问题的优质答案，文章，专栏文章，收藏夹的答案和文章',
    platforms='win10',
    install_requires=[
        'pygments>=2.3.1',
        'requests'
    ],
    scripts=[],
    entry_points={
        'console_scripts': [
            'zhihu = zhihu.GrandConcourse:main'
        ]
    },
    data_files=[
        ('zhihu/documen/attachment', ['zhihu/document/attachment/element.html',
                                      'zhihu/document/attachment/styleCode.css',
                                      'zhihu/document/attachment/styleMod.css',
                                      'zhihu/document/attachment/styleText.css'])
    ],
    zip_safe=False
)
