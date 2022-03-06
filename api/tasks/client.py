import functools
import logging
from typing import Callable
from typing import TypedDict
from typing import TypeVar
from unittest.mock import sentinel

import requests
from django.conf import settings
from typing_extensions import NotRequired


class TasksApiException(Exception):
    pass


log = logging.getLogger(__name__)
sentinel = object()

C = TypeVar("C", bound=Callable)


def json_or_raise(method: C) -> C:
    @functools.wraps(method)
    def inner(*args, **kwargs):
        try:
            response = method(*args, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            log.exception(f"failed to perform: {method.__name__}", e)
            raise TasksApiException(e.args)

    return inner  # noqa


class TaskResponse(TypedDict):
    task_id: str
    name: str
    status: int
    processing_time: int
    meta: dict


class TaskUpdatePayload(TypedDict):
    status: int
    meta: NotRequired[dict]


class TasksApiClient:
    base_url = f"{settings.API_HOST}/api/tasks"

    @json_or_raise
    def read_task(self, id: str) -> TaskResponse:
        url = f"{self.base_url}/{id}/"
        return requests.get(url, timeout=30)

    @json_or_raise
    def update_task(self, task_id: str, payload: TaskUpdatePayload) -> TaskResponse:
        url = f"{self.base_url}/{task_id}/"
        return requests.patch(url, json=payload, timeout=30)
