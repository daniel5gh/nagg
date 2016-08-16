# vim:set ft=dockerfile:
# This docker image is not suitable for production setups!
# - it includes all kinds of development related packages not required
#   during a standard production run
# - django secret key always has same value
# - django runserver is used
# The purpose of this image is to provide a development environment and
# has all development dependencies to build a wheel package of NAGG, which
# could then be installed in a production suitable setup.
FROM phusion/baseimage:0.9.19

RUN apt-get update && apt-get upgrade -y -o Dpkg::Options::="--force-confold"
# git needed to install some python requirements from github
# pkg-config (https://github.com/matplotlib/matplotlib/issues/3029/),
# libfreetype6 and libpng for matplotlib
# libpq-dev for psycopg2
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-pip git libfreetype6-dev libpng-dev pkg-config libpq-dev
# first only add requirements instead of the complete source dir, this
# prevents invalidating cache of the (long running) install when
# unrelated files change.
RUN mkdir /nagg_src
ADD requirements.txt /nagg_src
RUN set -x \
    && pip3 install virtualenv \
    && virtualenv -p /usr/bin/python3 /nagg_ve \
    && /nagg_ve/bin/pip install -r /nagg_src/requirements.txt

# TODO: move up
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y netcat
# TODO: pin in requirements, celery is not compatible with 1.10
RUN /nagg_ve/bin/pip install django==1.9

# install nodejs for npm and later on webpack!
ADD docker/nagg_app/nodesource.gpg.key /
RUN     set -x \
    && echo 'deb https://deb.nodesource.com/node_6.x xenial main' > /etc/apt/sources.list.d/nodesource.list \
    && apt-key add /nodesource.gpg.key \
    && rm -rf /nodesource.gpg.key \
    && apt-get -y update \
    && DEBIAN_FRONTEND=noninteractive apt-get -y install nodejs

# use 1000, convinient because I am 1000 too, yay!
RUN groupadd -r nagg -g 1000 && useradd -r -u 1000 -g nagg nagg && mkdir -p /home/nagg && chown 1000:1000 /home/nagg

ENV PYTHONUNBUFFERED 1
ENV DB_SERVICE_PORT=5432
ENV DB_SERVICE_HOST=db
ENV DB_NAME=nagg_db
ENV REDIS_SERVICE_PORT=6379
ENV REDIS_SERVICE_HOST=redis

# init scripts
ADD docker/nagg_app/wait_db.sh /etc/my_init.d/10_wait_db
ADD docker/nagg_app/migrate_db.sh /etc/my_init.d/20_migrate_db

# install runit services
RUN   set -x \
    && mkdir /etc/service/runserver \
    && mkdir /etc/service/celery-beat \
    && mkdir /etc/service/celery-worker

# django runservice
ADD docker/nagg_app/runserver.sh /etc/service/runserver/run

# install celery beat runit service
ADD docker/nagg_app/celery-beat.sh /etc/service/celery-beat/run

# conveniently run celery in the same container, production setups may
# want to separate the workers
ADD docker/nagg_app/celery-worker.sh /etc/service/celery-worker/run

ADD docker/nagg_app/activate_nagg_env.sh /

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# current dir contents changes often, so we put this towards the
# botoom of the dockerfile to prevent caches from being invalidated
ADD . /nagg_src
RUN  set -x \
    && chown -R nagg:nagg /nagg_src/ \
    && cd /nagg_src/ \
    && /nagg_ve/bin/python setup.py develop

# not needed right now, we're mounting hosts code anyway
#USER nagg
#RUN ls -la /
#RUN ls -la /nagg_src/
#RUN ls -la /nagg_src/static_root
#RUN ls -la /nagg_src/static_root/node_modules
#RUN cd /nagg_src/static_root && npm install
#USER root

# clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
