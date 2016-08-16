#!/usr/bin/env bash

echo "starting celery beat"
CMD="/nagg_ve/bin/nagg_manage celery beat --pidfile=/tmp/nagg-beat.pid --workdir=/nagg_src -l DEBUG"
exec su -c "${CMD}" -s /bin/sh nagg
