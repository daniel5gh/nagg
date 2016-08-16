================
News Aggregator!
================

Dev Quick Start
===============

1. Install docker engine and docker compose
#. docker-compose build
#. docker-compose up
#. when postgresql errors, CTRL-C and re-run docker-compose up

Browse to `the application <http://localhost:8000/>`_. No news items are
visible yet because the celery task that leeches new entries has not run
yet. You can initiate a leech run::

  # in a new terminal
  $ docker-compose exec nagg_app bash
  root@17f8c7449778:/#  ./activate_nagg_env.sh
  bash: cannot set terminal process group (1187): Inappropriate ioctl for device
  bash: no job control in this shell
  (nagg_ve) nagg@17f8c7449778:/$ nagg_manage nagg_run

Now observe lots of output on the terminal that is running the
`docker-compose up`.

Contents
========

==================== =========================================================
Path                 Description
==================== =========================================================
brains               ML stuff / common pyspark functions
django_nagg          Django main project dir
doc                  Sphinx (API) docs
docker               Dockerfile and scripts
mainpage             Django app Web-UI
nagg                 Django app data acquire / storage
shell_ipynb          IPython notebooks with random experiments
static_root          Static files, served by django's runserver. contains 3rd party JS
==================== =========================================================

Notes
=====

There are hardcoded paths!

1. docker-compose volumes
#. findspark in `brains/spark_common.py`
#. IPython notebooks

Hardcoded UID / GID (1000) for the nagg user in Dockerfile for great convenience
when mounting code from host!