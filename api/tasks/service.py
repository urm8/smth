from datetime import timedelta

from tasks import selectors
from tasks.models import Task
from tasks.schema import TaskIn


def create_task(payload: TaskIn) -> Task:
    task_type = selectors.read_task_type(payload.name)
    return Task.objects.create(task_type=task_type, time_to_process=timedelta(seconds=payload.processing_time))
