#!/usr/bin/env bash

echo "starting runserver"
CMD="/nagg_ve/bin/nagg_manage runserver 0.0.0.0:8000"
exec su -c "${CMD}" -s /bin/sh nagg
