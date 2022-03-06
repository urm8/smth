import sys

if "celery" in sys.argv:
    from gevent import monkey

    monkey.patch_all()
import logging
import os

from celery import Celery

# set the default Django settings module for the 'celery' program.


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tasks_api.settings")

CELERY_BROKER_URL = os.environ.get("BROKER_URI")

app = Celery("tasks_service", broker=CELERY_BROKER_URL)

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logging.info(f"Request: {self.request!r}")
