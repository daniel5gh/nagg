#!/usr/bin/env bash

echo "starting celery worker"
CMD="/nagg_ve/bin/nagg_manage celery worker --pidfile=/tmp/nagg-worker.pid --workdir=/nagg_src -l DEBUG"
exec su -c "${CMD}" -s /bin/sh nagg
