# coding=utf-8
import os

from youtube_dl.utils import DEFAULT_OUTTMPL
from celery.utils.log import get_task_logger
import youtube_dl

from django_nagg import celery_app

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
