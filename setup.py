from setuptools import setup
import zhihu

setup(
    name='Zhihu Spider',
    version=zhihu.__version__,
    keyword=('zhihu', 'spider'),
    packages=['zhihu', 'zhihu.md', 'zhihu.conf', 'zhihu.html',
              'zhihu.timer', 'zhihu.spider'],
    url='https://github.com/Milloyy/ZhihuSpider',
    license='MIT',
    author='Milloy',
    author_email='yuerxmm@163.com',
    description='Show zhihu answer, question and article as html or markdown file.',
    platforms='win10',
    install_requires=[
        'pygments>=2.3.1',
        'bs4',
        'requests'
    ],
    scripts=[],
    entry_points={
        'console_scripts': [
            'zhihu = zhihu.GrandConcourse:main'
        ]
    },
    data_files=[
        ('zhihu', ['zhihu/conf/config'])
    ],
    zip_safe=False
)
