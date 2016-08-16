#!/usr/bin/env bash

wait_for_db () {
    # wait for DB service to start accepting connections
    while ! nc -z ${DB_SERVICE_HOST} ${DB_SERVICE_PORT}; do
        sleep 0.2
    done
    echo "db ready"
}

wait_for_db