# coding=utf-8
from setuptools import setup

setup(
    name='nagg',
    version='0.1',
    packages=['nagg'],
    url='http://spiet.nl/',
    license='No',
    author='Daniel van Adrichem',
    author_email='daniel5nagg@spiet.nl',
    description='News Agg',
    entry_points={
        'console_scripts': [
            'nagg_run = nagg.leecher:main',
        ]
    },
    requires=['feedparser', 'requests', 'sqlalchemy']
)
