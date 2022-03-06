from uuid import UUID

from django.db import transaction

from tasks import selectors
from tasks.models import Task
from tasks.schema import TaskIn
from tasks.schema import TaskUpdate
from tasks.tasks import process_task


def create_task(payload: TaskIn) -> Task:
    with transaction.atomic():
        task_type = selectors.read_task_type(payload.name)
        task = Task.objects.create(task_type=task_type, processing_time=payload.processing_time)
        process_task.delay(str(task.pk))
        return task


def update_task(task_id: UUID, payload: TaskUpdate) -> Task:
    with transaction.atomic():
        task = selectors.read_task(task_id)
        task.status = Task.Status(payload.status)
        task.meta.update(payload.meta)
        task.save()
        return task
