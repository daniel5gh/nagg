# coding=utf-8
import datetime
import logging
import re
from time import mktime
import bs4
import feedparser
import requests
from sqlalchemy import select, func
from nagg.db import DB

__author__ = 'daniel'
_log = logging.getLogger(__name__)


class BaseLeecher:
    plugin_name = 'base'

    # noinspection PyMethodMayBeStatic
    def leech_since(self, since_date):
        """Get stuff that is new since `date`"""
        pass

    def configure(self, data):
        raise NotImplementedError()


def _get_url_content(url):
    head = {
        'User-Agent': 'Wget/1.13.4 (linux-gnu)',
        'Connection': 'Close',
        'Proxy-Connection': 'Keep-Alive'
    }
    return requests.get(url, headers=head).content


class URLLeecher(BaseLeecher):
    def __init__(self):
        super().__init__()
        self.url = None

    def configure(self, data):
        self.url = data['url']

    def get_url(self):
        return _get_url_content(self.url)


class FeedLeecher(URLLeecher):
    def leech_since(self, date):
        feed = feedparser.parse(self.get_url())
        return feed['items']


# noinspection PyUnresolvedReferences
class ArticleParserMixin:
    @staticmethod
    def _extract_from_node(node):
        ps = node.find_all('p')
        # noinspection PyProtectedMember
        a = '\n\n'.join([''.join([s for s in _._all_strings()]) for _ in ps])
        return a

    def parse_article(self, url):
        data = _get_url_content(url)
        soup = bs4.BeautifulSoup(data, "html.parser")
        node = soup.find_all(attrs={'class': 'article', 'itemprop': "articleBody"})[0]
        return self._extract_from_node(node)


class TweakersLeecher(ArticleParserMixin, FeedLeecher):
    plugin_name = 'tweakers-rss'

    def __init__(self):
        super().__init__()
        self.configure({
            'url': 'http://feeds.feedburner.com/tweakers/mixed'
        })

    def leech_since(self, since_date):
        items = super().leech_since(since_date)
        for item in items:
            date = item['published_parsed']
            date = datetime.datetime.fromtimestamp(mktime(date))
            if date > since_date:
                title = item['title']
                link = item['link']
                article = self.parse_article(link)
                content = '\n'.join([title, article])
                yield link, date, content
            else:
                _log.debug('out of date. ' + item['title'])


def _test_run():
    db = DB()
    l = TweakersLeecher()

    # get date of latest entry
    sel = select([func.max(db.news_items.c.publish_date).label('max_publish_date')])
    sel = sel.where(db.news_items.c.source_plugin == l.plugin_name)
    with db.engine.begin() as conn:
        max_publish_date = conn.execute(sel).scalar()
    if not max_publish_date:
        max_publish_date = datetime.datetime(1970, 1, 1)
    g = l.leech_since(max_publish_date)

    for item in g:
        print(item)
        db.insert_news_item(
            l.plugin_name,
            item[0],
            item[2],
            item[1]
        )


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    _test_run()
