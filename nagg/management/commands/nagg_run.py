# coding=utf-8
from nagg.leecher import LeechRunner

__author__ = 'daniel'

from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        # now do the things that you want with your models here
        lr = LeechRunner()
        lr.run()
