# coding=utf-8
import datetime
import logging
# import re
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

    def get_source_id(self):
        return self.plugin_name

    # noinspection PyMethodMayBeStatic
    def leech_since(self, since_date):
        """Get stuff that is new since `date`"""
        pass


def _get_url_content(url, type_=None):
    """Get content on given HTTP(S) url using Wget user agent"""
    head = {
        'User-Agent': 'Wget/1.13.4 (linux-gnu)',
        'Connection': 'Close',
        'Proxy-Connection': 'Keep-Alive'
    }
    if type_ == 'rss':
        head['Accept'] = 'application/rss+xml,application/rdf+xml,application/atom+xml,text/xml'

    return requests.get(url, headers=head).content


class URLLeecher(BaseLeecher):
    url = None

    def get_url_content(self):
        return _get_url_content(self.url)

    def get_source_id(self):
        return self.url


class FeedLeecher(URLLeecher):
    def leech_since(self, date):
        feed = feedparser.parse(self.get_url_content())
        return feed['items']


# noinspection PyUnresolvedReferences
class ArticleParserMixin:
    article_node_selector = {'class': 'article', 'itemprop': "articleBody"}

    @staticmethod
    def _extract_from_node(node):
        ps = node.find_all()
        # noinspection PyProtectedMember
        a = '\n\n'.join([''.join([s for s in _._all_strings()]) for _ in ps])
        return a

    def parse_article(self, url):
        data = _get_url_content(url)
        soup = bs4.BeautifulSoup(data, "html.parser")
        node = soup.find_all(attrs=self.article_node_selector)[0]
        return self._extract_from_node(node)


# noinspection PyMethodMayBeStatic
class GenericRSSLeecher(ArticleParserMixin, FeedLeecher):
    plugin_name = 'generic-rss'

    def extract_title(self, item):
        title = item['title']
        return title

    def extract_date(self, item):
        date = item['published_parsed']
        date = datetime.datetime.fromtimestamp(mktime(date))
        return date

    def extract_link(self, item):
        link = item['link']
        return link

    def leech_since(self, since_date):
        items = super().leech_since(since_date)
        for item in items:
            date = self.extract_date(item)
            title = self.extract_title(item)
            if date > since_date:
                link = self.extract_link(item)
                article = self.parse_article(link)
                content = '\n\n'.join([title, article])
                yield link, date, content
            else:
                _log.debug('out of date. ' + title)


class TweakersLeecher(GenericRSSLeecher):
    article_node_selector = {'class': 'article', 'itemprop': "articleBody"}
    plugin_name = 'tweakers-rss'
    url = 'http://feeds.feedburner.com/tweakers/mixed'


class NosJournaalLeecher(GenericRSSLeecher):
    article_node_selector = {'class': 'article_textwrap'}
    plugin_name = 'nos-journaal-rss'
    url = 'http://feeds.nos.nl/nosjournaal'


class TelegraafBinnenlandLeecher(GenericRSSLeecher):
    article_node_selector = {'id': 'artikelKolom'}
    plugin_name = 'telegraaf-binnenland-rss'
    url = 'http://feeds.nos.nl/nosjournaal'


class LeechRunner:
    def __init__(self):
        super().__init__()
        self._db = DB()
        self._leechers = []
        self.load_config()

    def load_config(self):
        self._leechers.append(TweakersLeecher())
        self._leechers.append(NosJournaalLeecher())

    def run_one(self, leecher):
        source_id = leecher.get_source_id()
        # determine since date
        table = self._db.news_items
        sel = select([func.max(table.c.publish_date).label('max_publish_date')])
        sel = sel.where(table.c.source_plugin == source_id)
        with self._db.engine.begin() as conn:
            max_publish_date = conn.execute(sel).scalar()
        if not max_publish_date:
            max_publish_date = datetime.datetime(1970, 1, 1)

        _log.info("Since %s doing %s", max_publish_date, source_id)

        g = leecher.leech_since(max_publish_date)

        for item in g:
            _log.debug(item)
            self._db.insert_news_item(
                source_plugin=source_id,
                url=item[0],
                text=item[2],
                publish_date=item[1],
            )

    def run(self):
        for leecher in self._leechers:
            self.run_one(leecher)


def _dev_debug(url):
    feed = feedparser.parse(_get_url_content(url, 'rss'))
    return feed['items']

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    runner = LeechRunner()
    runner.run()
