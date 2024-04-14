import os
import sys

from django.conf import settings
from kombu import Queue, Exchange

timezone = 'Europe/Madrid'

# Celery Tasks configuration
task_default_queue = 'default_queue'
task_queues = (
    Queue('default_queue', Exchange('default_queue'), routing_key='default_queue'),
)
task_routes = {
    # Configure task routing here. eg.
}

# Broker config (Rabbit MQ)
RABBIT_HOSTNAME = 'rabbitmq:5672'
broker_url = 'amqp://{user}:{password}@{hostname}'.format(
    user=os.environ.get('RABBITMQ_DEFAULT_USER'),
    password=os.environ.get('RABBITMQ_DEFAULT_PASS'),
    hostname=RABBIT_HOSTNAME,
    vhost=os.environ.get('RABBIT_ENV_VHOST', '')
)

broker_pool_limit = 10
"""
The maximum number of connections that can be open in the connection pool.
The pool is enabled by default since version 2.5, with a default limit of ten connections. 
This number can be tweaked depending on the number of threads/green-threads (eventlet/gevent) using a connection. 
For example running eventlet with 1000 greenlets that use a connection to the broker,
 contention can arise and you should consider increasing the limit.
"""
broker_connection_timeout = 4.0
"""
Default: 4.0
The default timeout in seconds before we give up establishing a connection to the AMQP server. 
This setting is disabled when using gevent.
"""

broker_heartbeat = 120
"""

Default: 120.0 (negotiated by server).

Note: This value is only used by the worker, clients do not use a heartbeat at the moment.

It’s not always possible to detect connection loss in a timely manner using TCP/IP alone, 
so AMQP defines something called heartbeats that’s is used both by the client and the broker to detect if a connection was closed.

If the heartbeat value is 10 seconds, then the heartbeat will be monitored at the interval specified by the broker_heartbeat_checkrate setting 
(by default this is set to double the rate of the heartbeat value, so for the 10 seconds, the heartbeat is checked every 5 seconds).
"""

# Enable "publisher confirms" to allow application to be sure when a message has been sent
# http://www.rabbitmq.com/blog/2011/02/10/introducing-publisher-confirms/
# https://tech.labs.oliverwyman.com/blog/2015/04/30/making-celery-play-nice-with-rabbitmq-and-bigwig/
broker_transport_options = {'confirm_publish': True}

# >> Tuning rabbitmq performance
# experimental
task_default_delivery_mode = 'transient'
"""
Default: "persistent".
Can be transient (messages not written to disk) or persistent (written to disk).
"""

task_remote_tracebacks = True  # requires celery[tblib]

# Sensible settings for celery
task_always_eager = False

if 'test' in sys.argv or 'jenkins' in sys.argv or 'pytest' in sys.modules:
    task_always_eager = True

task_publish_retry = True
worker_disable_rate_limits = False

task_ignore_result = False
result_expires = 60 * 60 * 1  # 1 hour
"""
Time (in seconds, or a timedelta object) for when after stored task tombstones will be deleted.

A built-in periodic task will delete the results after this time (celery.backend_cleanup), a
ssuming that celery beat is enabled. The task runs daily at 4am.

A value of None or 0 means results will never expire (depending on backend specifications).
"""

# Policy of task ACK.
# > normal:
# task_acks_late = False
# task_reject_on_worker_lost = False
# > late with countermeasures
# task_acks_late = True
# task_reject_on_worker_lost = True
# > defensive:
task_acks_late = False
task_reject_on_worker_lost = True
# > historical:
# task_acks_late = True
# task_reject_on_worker_lost = False


# Don't use pickle as serializer, json is much safer
task_serializer = "msgpack"
result_serializer = "json"
accept_content = ['json', 'msgpack']
task_compression = 'gzip'

# worker_prefetch_multiplier = 1  # Defalt: 4. Set it to '1' to disable prefetching
# worker_max_tasks_per_child = 1  # Default: nolimit

# >> Events
# Send task-related events so that tasks can be monitored using tools like flower.
# Default: disabled. Expected override by `celery worker -E`
worker_send_task_events = True
# If enabled, a task-sent event will be sent for every task so tasks can be tracked before they’re consumed by a worker.
task_send_sent_event = True

# >> result_backend
# Default: No result backend enabled by default.
# The backend used to store task results (tombstones).
result_backend = settings.REDIS_CONNECTION_URL if settings.USE_REDIS else 'file:///celery_results'

# >> result_persistent
# Default: Disabled by default (transient messages).
# If set to True, result messages will be persistent. This means the messages won’t be lost after a broker restart.
# result_persistent = True

# >> worker_hijack_root_logger
# Default: True
# By default any previously configured handlers on the root logger will be removed.
# If you want to customize your own logging handlers, then you can disable this
# behavior by setting worker_hijack_root_logger = False.
worker_hijack_root_logger = True

# >> worker_redirect_stdouts_level
# Default: WARNING.
# The log level output to stdout and stderr is logged as. Can be one of DEBUG, INFO, WARNING, ERROR, or CRITICAL.
# worker_redirect_stdouts_level = 'DEBUG'
# worker_redirect_stdouts = True
RABBIT_HOSTNAME = "rabbitmq"
RABBIT_AMPQ_HOST = f"{RABBIT_HOSTNAME}:5672"
RABBIT_MANAGEMENT_HOST = f"{RABBIT_HOSTNAME}:15672"

RABBIT_USER = os.environ.get('RABBITMQ_DEFAULT_USER')
RABBIT_PASSWORD = os.environ.get('RABBITMQ_DEFAULT_PASS')
