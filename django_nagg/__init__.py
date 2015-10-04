# coding=utf-8
import os
import sys

# copy from manage.py
# we use this as entry point in setup
def manage():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_nagg.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)