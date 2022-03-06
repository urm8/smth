from uuid import uuid4

import pytest

from tasks.client import TasksApiClient
from tasks.client import TasksApiException
from tasks.factories import TaskFactory
from tasks.models import Task


@pytest.fixture
def client(live_server):
    return TasksApiClient(str(live_server))


@pytest.mark.userfixuters("client")
@pytest.mark.db
class TestClient:
    def test_read_task(self, client):
        task = TaskFactory.create()
        data = client.read_task(str(task.task_id))
        assert data["task_id"] == str(task.pk)
        assert data["status"] == task.status
        assert data["processing_time"] == task.processing_time
        assert data["name"] == task.task_type.name
        assert data["meta"] == task.meta

    def test_read_task_not_exist(self, client):
        with pytest.raises(TasksApiException):
            client.read_task(f"{uuid4()}")

    def test_update_task(self, client):
        task = TaskFactory.create(status=Task.Status.NEW.value)
        data = client.update_task(f"{task.task_id}", {"status": Task.Status.COMPLETED.value})
        assert data["task_id"] == str(task.pk)
        assert data["status"] == Task.Status.COMPLETED.value

        task.refresh_from_db()
        assert task.status == Task.Status.COMPLETED.value
