from datetime import timedelta
from uuid import UUID

from django.db import transaction

from tasks import selectors
from tasks.models import Task
from tasks.schema import TaskIn
from tasks.schema import TaskUpdate


def create_task(payload: TaskIn) -> Task:
    task_type = selectors.read_task_type(payload.name)
    return Task.objects.create(task_type=task_type, time_to_process=timedelta(seconds=payload.processing_time))


def update_task(task_id: UUID, payload: TaskUpdate) -> Task:
    with transaction.atomic():
        task = selectors.read_task(task_id)
        task.status = Task.Status(payload.status)
        task.meta.update(payload.meta)
        return task
