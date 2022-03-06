from datetime import timedelta
from functools import partial
from operator import attrgetter

from factory import Faker
from factory.declarations import Dict
from factory.declarations import LazyFunction
from factory.declarations import SubFactory
from factory.fuzzy import FuzzyChoice, FuzzyInteger

from base_factory import BaseFactory

from .models import Task
from .models import TaskType


class TaskTypeFactory(BaseFactory[TaskType]):
    class Meta:
        model = TaskType

    name = Faker("word")


class TaskFactory(BaseFactory[Task]):
    class Meta:
        model = Task

    task_type = SubFactory(TaskTypeFactory)
    processing_time = FuzzyInteger(low=0, high=100)
    status = FuzzyChoice(Task.Status, getter=attrgetter('value'))
    meta = Dict({"yay": "im a task!"})
