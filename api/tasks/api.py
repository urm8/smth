from typing import Iterable
from uuid import UUID

from ninja import Router

from tasks import selectors
from tasks import service

from .models import Task
from .models import TaskType
from .schema import IdName
from .schema import TaskBase
from .schema import TaskIn
from .schema import TaskOut
from .schema import TaskUpdate

router = Router()


@router.post("/", response={201: TaskBase})
def create_task(_, task_request: TaskIn):
    return 201, service.create_task(task_request)


@router.get("/", response=list[TaskOut])
def read_tasks(_) -> Iterable[Task]:
    return selectors.read_tasks()


@router.get("{task_id}/", response=TaskOut)
def read_task(_, task_id: UUID) -> Task:
    return selectors.read_task(task_id)


@router.patch("{task_id}/", response=TaskOut)
def update_task(request, task_id: UUID, payload: TaskUpdate):
    return service.update_task(task_id, payload)


suggest_router = Router(tags=["suggest"])
router.add_router("suggest", suggest_router)


@suggest_router.get("task-types/", response=list[IdName])
def suggest_task_type(_, q: str | None = None) -> Iterable[TaskType]:
    return selectors.suggest_task_type(q)
