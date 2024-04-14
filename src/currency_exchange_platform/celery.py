from __future__ import absolute_import

import celeryconfig
from celery import Celery

app = Celery('currency_exchange_platform')
app.config_from_object(celeryconfig)
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
