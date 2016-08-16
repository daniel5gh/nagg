#!/usr/bin/env bash

# activate virtual env as user nagg
CMD="bash --init-file /nagg_ve/bin/activate && cd /nagg_src"
exec su -s /bin/sh -c "${CMD}" nagg
