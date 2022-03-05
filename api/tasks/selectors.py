from typing import Iterable
from uuid import UUID

from django.shortcuts import get_object_or_404

from tasks.models import Task
from tasks.models import TaskType


def read_task_type(name: str) -> TaskType:
    return get_object_or_404(TaskType, name=name)


def suggest_task_type(query: str | None) -> Iterable[TaskType]:
    """basic like 'query%' search."""
    qs = TaskType.objects.all()
    if query:
        qs = qs.filter(name__istartswith=query)
    return qs


def read_tasks() -> Iterable[Task]:
    return Task.objects.select_related("task_type").all()


def read_task(pk: UUID) -> Task:
    return get_object_or_404(Task, pk=pk)
