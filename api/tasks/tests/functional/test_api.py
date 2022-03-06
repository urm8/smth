import json
from uuid import uuid4

import pytest

from tasks.factories import TaskFactory
from tasks.factories import TaskTypeFactory
from tasks.models import Task


@pytest.mark.userfixuters("client")
@pytest.mark.db
class TestTaskApi:
    def test_read_task(self, client):
        task = TaskFactory.create()
        response = client.get(f"/api/tasks/{task.task_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == str(task.pk)
        assert data["status"] == task.status
        assert data["processing_time"] == task.processing_time
        assert data["name"] == task.task_type.name
        assert data["meta"] == task.meta

    def test_read_task_not_exist(self, client):
        response = client.get(f"/api/tasks/{uuid4()}/")
        assert response.status_code == 404

    def test_read_tasks(self, client):
        tasks = TaskFactory.create_batch(size=2)
        response = client.get(f"/api/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(tasks)

    def test_update_task(self, client):
        task = TaskFactory.create(status=Task.Status.NEW.value)
        assert task.status == 1
        response = client.patch(
            f"/api/tasks/{task.task_id}/",
            json.dumps({"status": Task.Status.COMPLETED.value}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == str(task.pk)
        assert data["status"] == Task.Status.COMPLETED.value

        task.refresh_from_db()
        assert task.status == Task.Status.COMPLETED.value

    def test_create(self, client):
        task_type = TaskTypeFactory.create()
        expected_processing_time = 123
        assert not Task.objects.exists()
        response = client.post(
            f"/api/tasks/",
            json.dumps({"name": task_type.name, "processing_time": expected_processing_time}),
            content_type="application/json",
        )
        assert response.status_code == 201
        assert Task.objects.count() == 1
        data = response.json()
        assert len(data) == 1
        task_id = data["task_id"]
        task = Task.objects.get(task_id=task_id)
        assert task.status == Task.Status.NEW
        assert task.meta == {}
        assert task.processing_time == expected_processing_time
