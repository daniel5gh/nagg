# coding=utf-8
"""
A module that can leech internet resources. It is able to get new resources
since a specified :class:`datetime.datetime`.

:author: Daniël <daniel5git@spiet.nl>
"""
import datetime
import logging
from time import mktime
import bs4
import feedparser
import requests


from nagg.tasks import download_youtube, do_one_leecher

__author__ = 'daniel'
_log = logging.getLogger(__name__)


class BaseLeecher:
    """This class is the base for all leechers

    """
    plugin_name = 'base'

    def get_source_id(self) -> str:
        """Get an unique identifier for this leecher.  This will
        usually describe the source.

        :return: Leecher identifier
        :rtype: str
        """
        return self.plugin_name

    # noinspection PyMethodMayBeStatic
    def leech_since(self, since_date) -> tuple:
        """Get stuff that is new since `since_date`

        :type since_date: datetime.datetime
        :param since_date: new since :class:`datetime.datetime`
        :returns: :class:`generator` of dicts`
        :rtype: tuple
        """
        pass


def _get_url(url, type_=None, cookies=None):
    """Get content on given HTTP(S) url using Wget user agent.

    This method uses :mod:`requests` to make the request. The
    `type_` that is passed determines some behavior. Passing
    `rss` will set the `Accept` header to request
    `'application/rss+xml,application/rdf+xml,application/atom+xml,text/xml'`.

    :type url: str
    :param url: URL to fetch from
    :type type_: str
    :param type_: A string indicating the type of resource.
    :type cookies: dict
    :param cookies: Cookies to send with the request
    :returns: Response object
    :rtype: requests.Response
    """
    head = {
        'User-Agent': 'Wget/1.13.4 (linux-gnu)',
        'Connection': 'Close',
        'Proxy-Connection': 'Keep-Alive'
    }
    if type_ == 'rss':
        head['Accept'] = 'application/rss+xml,application/rdf+xml,application/atom+xml,text/xml'

    return requests.get(url, headers=head, cookies=cookies)


def _get_url_content(url, type_=None, cookies=None):
    """Like :func:`_get_url` but returns the resource content.

    :type url: str
    :param url: URL to fetch from
    :type type_: str
    :param type_: A string indicating the type of resource.
    :type cookies: dict
    :param cookies: Cookies to send with the request
    :rtype: bytes
    """
    return _get_url(url, type_, cookies).content


class URLLeecher(BaseLeecher):
    """This leecher is specialized to handle HTTP(S) URLs.

    The work horse behind this class is :mod:`requests`.
    """
    #: A :class:`str` containing URL we are leeching from
    url = None
    #: Affects the used `Accept` header. See :func:`_get_url` `type_` argument.
    url_accept_type = None
    #: A :class:`dict` with cookies to send with the HTTP request
    cookies = None

    def leech_since(self, since_date):
        """Get content from the :any:`URLLeecher.url` or passed url
        is it is given.

        :param since_date: See :any:`BaseLeecher.leech_since`.
        :return: See :any:`BaseLeecher.leech_since`.
        :rtype: tuple
        """

        url = self.url

        # noinspection PyTypeChecker
        r = _get_url(url, self.url_accept_type, self.cookies)
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
            yield {
                'url': url,
                'date': date,
                'content': r.content,
            }
        else:
            _log.debug('No new content: %s', url)

    def get_source_id(self):
        """Returns the url of the resource.

        :rtype: str
        """

        return self.url


class FeedLeecher(URLLeecher):
    """Leech a RSS feed.

    This uses the base :class:`URLLeecher` to fetch the URL content and
    then uses :mod:`feedparser` its :class:`feed` class to interpret
    and parse the data.

    The third item in the tuple, the content, is from `feedparser`.
    """
    url_accept_type = 'rss'

    def leech_since(self, since_date):
        """See base class"""
        for obj in super().leech_since(since_date):
            data = obj['content']
            if data:
                feed = feedparser.parse(data)
                for item in feed['items']:
                    yield {
                        'url': self.url,
                        'date': since_date,
                        'content': item,
                    }
            else:
                _log.debug('No new feed content: %s', self.url)


# noinspection PyUnresolvedReferences
class ArticleParserMixin:
    """Mixin that can parse text from a HTML article"""

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
        nodes = soup.find_all(attrs=self.article_node_selector)
        node = nodes[0]
        return self.extract_from_node(node)


# noinspection PyMethodMayBeStatic
class GenericRSSLeecher(FeedLeecher):
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

    def extract_content(self, item):
        summary = item.get('summary', None)
        return summary

    def leech_since(self, since_date):
        for obj in super().leech_since(since_date):
            item = obj['content']
            date = self.extract_date(item)
            title = self.extract_title(item)
            if date > since_date:
                link = self.extract_link(item)
                article = self.extract_content(item)
                content = '\n\n'.join([title, article])
                yield {
                    'url': link,
                    'date': date,
                    'content': content,
                }
#            else:
#                _log.debug('out of date. ' + title)


# noinspection PyMethodMayBeStatic
class GenericArticleLeecher(ArticleParserMixin, GenericRSSLeecher):
    plugin_name = 'generic-article-rss'

    def extract_content(self, item):
        link = self.extract_link(item)
        return self.parse_article(link)


class TweakersLeecher(GenericArticleLeecher):
    article_node_selector = {'class': 'article', 'itemprop': "articleBody"}
    plugin_name = 'tweakers-rss'
    url = 'http://feeds.feedburner.com/tweakers/mixed'


class NosJournaalLeecher(GenericArticleLeecher):
    article_node_selector = {'class': 'article_textwrap'}
    plugin_name = 'nos-journaal-rss'
    url = 'http://feeds.nos.nl/nosjournaal'


class TelegraafLeecher(GenericArticleLeecher):
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


class VolkskrantLeecher(GenericArticleLeecher):
    article_node_selector = {'class': 'article'}
    plugin_name = 'volkskrant-rss'
    cookies = {'nl_cookiewall_version': '1'}

    def extract_from_node(self, node):
        text = super().extract_from_node(node)
        # text has title twice, remove one
        parts = '\n'.join(text.split('\n'))
        if parts:
            return '\n'.join(text.split('\n')[1:])
        else:
            return text


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


class ADLeecher(GenericArticleLeecher):
    article_node_selector = {'class': 'article'}
    plugin_name = 'ad-rss'
    cookies = {'nl_cookiewall_version': '1'}


class ADDenHaagLeecher(ADLeecher):
    url = 'http://www.ad.nl/cache/rss_nederland_den_haag.xml'


class ADNieuwsLeecher(ADLeecher):
    url = 'http://www.ad.nl/rss.xml'


class TrouwLeecher(GenericArticleLeecher):
    article_node_selector = {'id': 'art_box2'}
    plugin_name = 'trouw-rss'
    cookies = {'nl_cookiewall_version': '1'}


class TrouwNieuwsLeecher(TrouwLeecher):
    url = 'http://www.trouw.nl/nieuws/rss.xml'


class OverheidDataLeecher(GenericArticleLeecher):
    article_node_selector = {'class': 'module'}
    plugin_name = 'overhheid-data-rss'
    url = 'https://data.overheid.nl/data/feeds/dataset.atom'

    def extract_from_node(self, node):
        text = super().extract_from_node(node)
        # text has title twice, remove one
        parts = '\n'.join(text.split('\n'))
        if parts:
            return '\n'.join(text.split('\n')[1:])
        else:
            return text


class YoutubeRSSLeecher(GenericRSSLeecher):
    plugin_name = 'youtube-rss'

    def __init__(self, *, url, source):
        self.url = url
        self.source = source

    def get_source_id(self):
        return 'YouTube - {}'.format(self.source)

    def leech_since(self, since_date):
        for obj in super().leech_since(since_date):
            yield obj
            download_youtube.delay(obj['url'])


class LeechRunner:
    def __init__(self):
        super().__init__()
        self._leechers = []
        self.load_config()

    def load_config(self):
        self._leechers.append(OverheidDataLeecher())
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
        for url, source in (
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UC7DdEm33SyaTDtWYGO2CwdA', 'Physics Girl'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UCvBqzzvUBLCs8Y7Axb-jZew', 'Sixty Symbols'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UCUHW94eEFW7hkUMVaZz4eDg', 'MinutePhysics'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UCUK0HBIBWgM2c4vsPhkYY4w', 'The Slow Mo Guys'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UC6nSFpj9HTCZ5t-N3Rm3-HA', 'Vsauce'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UCHnyfMqiRRG1u-2MsSQLbXA', 'Veritasium'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UCCAgrIbwcJ67zIow1pNF30A', 'nottinghamscience'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UCo-3ThNQmPmQSQL_L6Lx1_w', 'DeepSkyVideos'),
            # ('https://www.youtube.com/feeds/videos.xml?channel_id=UC2DjFE7Xf11URZqWBigcVOQ', 'EEVblog'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UCtESv1e7ntJaLJYKIO1FoYw', 'Periodic Videos'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UCivA7_KLKWo43tFcCkFvydw', 'Applied Science'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UCoxcjq-8xIDTYp3uz647V5A', 'Numberphile'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UC6107grRI4m0o2-emgoDnAA', 'SmarterEveryDay'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UCrMePiHCWG4Vwqv3t7W9EFg', 'SciShow Space'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UCM-p4l2OPH_oX6tFrjKT-9A', 'Year In Space'),
            ('https://www.youtube.com/feeds/videos.xml?channel_id=UC9-y-6csu5WGm29I7JiwpnA', 'Computerphile'),
        ):
            self._leechers.append(YoutubeRSSLeecher(url=url, source=source))

    def run(self):
        for leecher in self._leechers:
            do_one_leecher.delay(leecher)


def _dev_debug(url):
    feed = feedparser.parse(_get_url_content(url, 'rss'))
    return feed['items']
