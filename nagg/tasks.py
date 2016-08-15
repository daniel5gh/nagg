# coding=utf-8
import os
import datetime

from youtube_dl.utils import DEFAULT_OUTTMPL
from django.db.models import Max
from django.utils import timezone
from celery.utils.log import get_task_logger
import youtube_dl

from django_nagg import celery_app
from .models import NewsItem

__author__ = 'daniel'
_log = get_task_logger(__name__)

DOWNLOAD_PATH = '/dream/nagg_download'


@celery_app.task(bind=True)
def download_youtube(self, url):
    _log.info('Download {}'.format(url))
    ydl_opts = {
        'logger': _log,
        # 'download_archive': os.path.join(DOWNLOAD_PATH, 'yt_download_archive'),
        'outtmpl': os.path.join(DOWNLOAD_PATH, '%(uploader)s', DEFAULT_OUTTMPL),
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        # 'skip_download': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


@celery_app.task(bind=True)
def do_one_leecher(self, leecher):
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
                url=item['url'],
                text=item['content'],
                publish_date=item['date'],
                retrieval_date=timezone.now()
            )
            ni.save()
            i += 1
        _log.info('Adding %d from %s', i, source_id)
    except Exception:
        _log.exception('Error doing %s', source_id)
        raise
