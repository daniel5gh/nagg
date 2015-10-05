# coding=utf-8
import datetime
from datetime import tzinfo
import logging
# import re
from time import mktime
import bs4
import feedparser
import requests

from sqlalchemy import select, func
from django.db.models import Max
from django.utils import timezone

from nagg.db import DB
from nagg.models import NewsItem

__author__ = 'daniel'
_log = logging.getLogger(__name__)


class BaseLeecher:
    plugin_name = 'base'

    def get_source_id(self):
        return self.plugin_name

    # noinspection PyMethodMayBeStatic
    def leech_since(self, since_date):
        """Get stuff that is new since `date`"""
        # link, date, content
        return None, None, None


def _get_url(url, type_=None, cookies=None):
    """Get content on given HTTP(S) url using Wget user agent"""
    head = {
        'User-Agent': 'Wget/1.13.4 (linux-gnu)',
        'Connection': 'Close',
        'Proxy-Connection': 'Keep-Alive'
    }
    if type_ == 'rss':
        head['Accept'] = 'application/rss+xml,application/rdf+xml,application/atom+xml,text/xml'

    return requests.get(url, headers=head, cookies=cookies)


def _get_url_content(url, type_=None, cookies=None):
    return _get_url(url, type_, cookies).content


class URLLeecher(BaseLeecher):
    url = None
    url_accept_type = None
    cookies = None

    def leech_since(self, since_date):
        r = _get_url(self.url, self.url_accept_type, self.cookies)
        date = r.headers.get('last-modified', None)
        if date:
            # noinspection PyProtectedMember
            date = feedparser._parse_date(date)
            date = datetime.datetime.fromtimestamp(mktime(date),
                                                   tz=datetime.timezone.utc)
            _log.debug('http modified date: %s', date)
        else:
            date = since_date
        if date >= since_date:
            return self.url, date, r.content
        else:
            _log.debug('No new content: %s', self.url)
            return None, None, None

    def get_source_id(self):
        return self.url


class FeedLeecher(URLLeecher):
    url_accept_type = 'rss'

    def leech_since(self, since_date):
        _, _, data = super().leech_since(since_date)
        if data:
            feed = feedparser.parse(data)
            return self.url, since_date, feed['items']
        else:
            _log.debug('No new feed content: %s', self.url)
            return None, None, []


# noinspection PyUnresolvedReferences
class ArticleParserMixin:
    article_node_selector = {'class': 'article', 'itemprop': "articleBody"}

    # this will be passed the node identified by article_node_selector
    def extract_from_node(self, node):
        nodes = []
        nodes.extend(node.find_all('h1'))
        nodes.extend(node.find_all('p'))
        return self._extract_all_strings(nodes)

    @staticmethod
    def _extract_all_strings(nodes):
        # noinspection PyProtectedMember
        return '\n\n'.join([''.join([s for s in _._all_strings()]) for _ in nodes])

    def parse_article(self, url):
        data = _get_url_content(url, cookies=self.cookies)
        soup = bs4.BeautifulSoup(data, "html.parser")
        node = soup.find_all(attrs=self.article_node_selector)[0]
        return self.extract_from_node(node)


# noinspection PyMethodMayBeStatic
class GenericRSSLeecher(ArticleParserMixin, FeedLeecher):
    plugin_name = 'generic-rss'

    def extract_title(self, item):
        title = item['title']
        return title

    def extract_date(self, item):
        date = item['published_parsed']
        date = datetime.datetime.fromtimestamp(mktime(date),
                                               tz=datetime.timezone.utc)
        return date

    def extract_link(self, item):
        link = item['link']
        return link

    def extract_content(self, link):
        return self.parse_article(link)

    def leech_since(self, since_date):
        _, _, items = super().leech_since(since_date)
        if items is None:
            items = []
        for item in items:
            date = self.extract_date(item)
            title = self.extract_title(item)
            if date > since_date:
                link = self.extract_link(item)
                article = self.extract_content(link)
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


class TelegraafLeecher(GenericRSSLeecher):
    article_node_selector = {'id': 'artikel'}
    plugin_name = 'telegraaf-rss'


class TelegraafBinnenlandLeecher(TelegraafLeecher):
    url = 'http://www.telegraaf.nl/rss/binnenland.xml'


class TelegraafBuitenlandLeecher(TelegraafLeecher):
    url = 'http://www.telegraaf.nl/rss/buitenland.xml'


class TelegraafDigitaalLeecher(TelegraafLeecher):
    url = 'http://www.telegraaf.nl/rss/digitaal.xml'


class TelegraafGamesLeecher(TelegraafLeecher):
    url = 'http://www.telegraaf.nl/rss/digitaal.games.xml'


class VolkskrantLeecher(GenericRSSLeecher):
    article_node_selector = {'class': 'article'}
    plugin_name = 'volkskrant-rss'
    cookies = {'nl_cookiewall_version': '1'}

    def extract_from_node(self, node):
        text = super().extract_from_node(node)
        # text has title twice, remove one
        return '\n'.join(text.split('\n')[1:])


class VolkskrantNieuwsLeecher(VolkskrantLeecher):
    url = 'http://www.volkskrant.nl/nieuws/rss.xml'


class VolkskrantBinnenlandLeecher(VolkskrantLeecher):
    url = 'http://www.volkskrant.nl/nieuws/binnenland/rss.xml'


class VolkskrantBuitenlandLeecher(VolkskrantLeecher):
    url = 'http://www.volkskrant.nl/nieuws/buitenland/rss.xml'


class VolkskrantTechLeecher(VolkskrantLeecher):
    url = 'http://www.volkskrant.nl/tech-media/rss.xml'


class VolkskrantWetenschapLeecher(VolkskrantLeecher):
    url = 'http://www.volkskrant.nl/nieuws/gezondheidwetenschap/rss.xml'


class ADLeecher(GenericRSSLeecher):
    article_node_selector = {'class': 'article'}
    plugin_name = 'ad-rss'
    cookies = {'nl_cookiewall_version': '1'}


class ADDenHaagLeecher(ADLeecher):
    url = 'http://www.ad.nl/cache/rss_nederland_den_haag.xml'


class ADNieuwsLeecher(ADLeecher):
    url = 'http://www.ad.nl/rss.xml'


class TrouwLeecher(GenericRSSLeecher):
    article_node_selector = {'id': 'art_box2'}
    plugin_name = 'trouw-rss'
    cookies = {'nl_cookiewall_version': '1'}


class TrouwNieuwsLeecher(TrouwLeecher):
    url = 'http://www.trouw.nl/nieuws/rss.xml'


class LeechRunnerSQLAlchemy:
    def __init__(self):
        super().__init__()
        self._db = DB()
        self._leechers = []
        self.load_config()

    def load_config(self):
        self._leechers.append(TrouwNieuwsLeecher())
        self._leechers.append(ADDenHaagLeecher())
        self._leechers.append(ADNieuwsLeecher())
        self._leechers.append(VolkskrantNieuwsLeecher())
        self._leechers.append(VolkskrantBinnenlandLeecher())
        self._leechers.append(VolkskrantTechLeecher())
        self._leechers.append(VolkskrantWetenschapLeecher())
        self._leechers.append(TweakersLeecher())
        self._leechers.append(NosJournaalLeecher())
        self._leechers.append(TelegraafBinnenlandLeecher())
        self._leechers.append(TelegraafBuitenlandLeecher())
        self._leechers.append(TelegraafDigitaalLeecher())
        self._leechers.append(TelegraafGamesLeecher())

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

        # noinspection PyBroadException
        try:
            g = leecher.leech_since(max_publish_date)
            i = 0
            for item in g:
                _log.debug(item)
                self._db.insert_news_item(
                    source_plugin=source_id,
                    url=item[0],
                    text=item[2],
                    publish_date=item[1],
                )
                i += 1
            _log.info('Added %d', i)
        except Exception:
            _log.exception('Error doing %s', source_id)
            raise

    def run(self):
        for leecher in self._leechers:
            self.run_one(leecher)


class LeechRunner:
    def __init__(self):
        super().__init__()
        self._leechers = []
        self.load_config()

    def load_config(self):
        self._leechers.append(TrouwNieuwsLeecher())
        self._leechers.append(ADDenHaagLeecher())
        self._leechers.append(ADNieuwsLeecher())
        self._leechers.append(VolkskrantNieuwsLeecher())
        self._leechers.append(VolkskrantBinnenlandLeecher())
        self._leechers.append(VolkskrantTechLeecher())
        self._leechers.append(VolkskrantWetenschapLeecher())
        self._leechers.append(TweakersLeecher())
        self._leechers.append(NosJournaalLeecher())
        self._leechers.append(TelegraafBinnenlandLeecher())
        self._leechers.append(TelegraafBuitenlandLeecher())
        self._leechers.append(TelegraafDigitaalLeecher())
        self._leechers.append(TelegraafGamesLeecher())

    @staticmethod
    def run_one(leecher):
        source_id = leecher.get_source_id()
        # determine since date
        max_publish_date = NewsItem.objects.filter(
            source=source_id).aggregate(Max('publish_date'))['publish_date__max']

        if not max_publish_date:
            max_publish_date = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

        _log.info("Since %s doing %s", max_publish_date, source_id)

        # noinspection PyBroadException
        try:
            g = leecher.leech_since(max_publish_date)
            i = 0
            for item in g:
                _log.debug(item)
                ni = NewsItem(
                    source=source_id,
                    url=item[0],
                    text=item[2],
                    publish_date=item[1],
                    retrieval_date=timezone.now()
                )
                ni.save()
                i += 1
            _log.info('Adding %d', i)
        except Exception:
            _log.exception('Error doing %s', source_id)
            raise

    def run(self):
        for leecher in self._leechers:
            self.run_one(leecher)


def _dev_debug(url):
    feed = feedparser.parse(_get_url_content(url, 'rss'))
    return feed['items']


def main():
    # logging.basicConfig(level=logging.INFO)
    runner = LeechRunnerSQLAlchemy()
    runner.run()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
