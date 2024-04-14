#!/bin/bash

if [ ! -v WORKER_NAME ]; then
  echo '   You must define WORKER_NAME - a name for the worker.'
  exit 1
fi

if [ ! -v WORKER_QUEUES ]; then
  WORKER_QUEUES=$WORKER_NAME
fi

if [ ! -v WORKER_CONCURRENCY ]; then
  WORKER_CONCURRENCY=1
fi

cat <<EOF

## DEPLOY: BEGIN RUN STEP ##
running "$0" at $(date)
EOF

set -eux

# setting broad permissions to share volumes
umask 000

# Wait for services
dockerize -wait tcp://rabbitmq:5672 -timeout 30s
dockerize -wait tcp://currency_platform_postgres:5432 -timeout 30s


echo "> Starting worker '$WORKER_NAME'..."
celery \
  -A celery worker \
  -E \
  -Ofair \
  -n $WORKER_NAME \
  --loglevel=INFO \
  --logfile=/logs/%p.log \
  --without-gossip \
  --without-mingle \
  -c $WORKER_CONCURRENCY \
  -Q $WORKER_QUEUES \
  -P prefork
