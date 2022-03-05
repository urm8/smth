from uuid import uuid4

from django.db import models


class ModelBase(models.Model):
    class Meta:
        abstract = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.pk})"


class TaskType(ModelBase):
    name = models.CharField(max_length=256, verbose_name="human readable task name", unique=True)


class Task(ModelBase):
    class Status(models.IntegerChoices):
        NEW = 1
        PROCESSING = 2
        COMPLETED = 3
        ERROR = 4

    task_id = models.UUIDField(default=uuid4, primary_key=True, db_column="id")
    task_type = models.ForeignKey(TaskType, on_delete=models.PROTECT)
    processing_time = models.IntegerField(verbose_name="time to process")
    status = models.IntegerField(choices=Status.choices, default=Status.NEW)
    meta = models.JSONField(default=dict)
