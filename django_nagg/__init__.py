# coding=utf-8
import os
import sys


# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

# copy from manage.py
# we use this as entry point in setup
def manage():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_nagg.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)