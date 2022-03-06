import logging

import gevent
from celery import shared_task

from tasks.client import TasksApiClient
from tasks.client import TasksApiException
from tasks.client import TaskUpdatePayload

UNLUCKY = 13
log = logging.getLogger(__name__)


class UnluckyException(Exception):
    pass


@shared_task
def process_task(task_id: str) -> None:
    log.info("processing: task(%s)", task_id)
    client = TasksApiClient()
    try:
        task = client.read_task(task_id)
        task = client.update_task(task_id, {"status": 2})
        processing_time = task["processing_time"]
        gevent.sleep(processing_time)

        if processing_time == UNLUCKY:
            raise UnluckyException("unlucky 😔")
        payload: TaskUpdatePayload = {"status": 3}
        log.info("update: task(%s), payload: %s", task_id, payload)
        client.update_task(task_id, payload)
        log.info("success: task(%s)", task_id)
    except (TasksApiException, UnluckyException) as e:
        log.exception("failure: task(%s), error(%s)", task_id, e)
        client.update_task(task_id, {"status": 4})
