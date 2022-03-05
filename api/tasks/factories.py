from datetime import timedelta
from functools import partial

from factory import Faker
from factory.declarations import Dict
from factory.declarations import LazyFunction
from factory.declarations import SubFactory

from base_factory import BaseFactory

from .models import Task
from .models import TaskType


class TaskRegistryFactory(BaseFactory[TaskType]):
    class Meta:
        model = TaskType

    name = Faker("word")


class TaskFactory(BaseFactory[Task]):
    class Meta:
        model = Task

    task_type = SubFactory(TaskRegistryFactory)
    time_to_process = LazyFunction(partial(timedelta, seconds=30))
    meta = Dict({"yay": "im a task!"})
