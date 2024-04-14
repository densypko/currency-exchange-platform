#!/bin/bash

cat <<EOF

## DEPLOY: BEGIN RUN STEP ##
running "$0" at $(date)
EOF

set -eux

# setting broad permissions to share volumes
umask 000

# Wait for services
dockerize -wait tcp://rabbitmq:5672 -timeout 30s

sleep 5
echo "> Starting flower..." # Start after workers
celery -A celery flower \
  --conf=conf/flowerconfig.py \
  --loglevel=info \
  --without-gossip \
  --without-mingle \
  --port="${FLOWER_PORT:-5556}" \
  --address=0.0.0.0 \
  --url-prefix=flower \
  --max_tasks=1000 \
  --inspect_timeout=30000 \
  --logfile="/logs/flower.log"
