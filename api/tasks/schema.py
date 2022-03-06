from uuid import UUID

from ninja import Field
from ninja import Schema


class IdName(Schema):
    id: str
    name: str


class TaskIn(Schema):
    name: str
    processing_time: int


class TaskBase(Schema):
    task_id: UUID


class TaskOut(TaskIn, TaskBase):
    name: str = Field(..., alias="task_type.name")
    status: int
    meta: dict


class TaskUpdate(Schema):
    status: int
    meta: dict = Field(default_factory=dict)
