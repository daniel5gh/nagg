#!/usr/bin/env bash

echo "migrating db"
CMD="/nagg_ve/bin/nagg_manage migrate"
exec su -c "${CMD}" -s /bin/sh nagg
