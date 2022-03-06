from unittest import mock
from unittest.mock import call

import pytest

from tasks.client import TasksApiClient
from tasks.client import TasksApiException
from tasks.factories import TaskFactory
from tasks.models import Task
from tasks.schema import TaskOut
from tasks.tasks import process_task


@pytest.fixture
def task(request):
    kwargs = dict(processing_time=1, status=Task.Status.NEW.value)
    kwargs.update(getattr(request, "param", {}))
    task = TaskFactory.build(**kwargs)
    return task


@pytest.mark.usefixtures("task")
class TestProcessTask:
    def test_works(self, task):
        task_dict = TaskOut.from_orm(task).dict()
        m = process_task.__module__
        with mock.patch(
            f"{m}.TasksApiClient", return_value=mock.MagicMock(spec=TasksApiClient)
        ) as mock_client_class, mock.patch(f"{m}.gevent") as mock_gevent:
            mock_client = mock_client_class.return_value
            mock_client.read_task.return_value = task_dict
            mock_client.update_task.return_value = {**task_dict, "status": Task.Status.PROCESSING.value}
            process_task(str(task.task_id))
            mock_gevent.sleep.assert_called_once_with(task.processing_time)
            mock_client.read_task.assert_called_once_with(str(task.task_id))
            assert mock_client.update_task.call_count == 2
            mock_client.update_task.assert_has_calls(
                [
                    call(str(task.task_id), {"status": Task.Status.PROCESSING.value}),
                    call(str(task.task_id), {"status": Task.Status.COMPLETED.value}),
                ]
            )

    @pytest.mark.parametrize("task", [{"processing_time": 13}], indirect=True)
    def test_unlucky(self, task):
        task_dict = TaskOut.from_orm(task).dict()
        m = process_task.__module__
        with mock.patch(
            f"{m}.TasksApiClient", return_value=mock.MagicMock(spec=TasksApiClient)
        ) as mock_client_class, mock.patch(f"{m}.gevent") as mock_gevent:
            mock_client = mock_client_class.return_value
            mock_client.read_task.return_value = task_dict
            mock_client.update_task.return_value = {**task_dict, "status": Task.Status.PROCESSING.value}
            process_task(str(task.task_id))
            mock_gevent.sleep.assert_called_once_with(task.processing_time)
            mock_client.read_task.assert_called_once_with(str(task.task_id))
            assert mock_client.update_task.call_count == 2
            mock_client.update_task.assert_has_calls(
                [
                    call(str(task.task_id), {"status": Task.Status.PROCESSING.value}),
                    call(str(task.task_id), {"status": Task.Status.ERROR.value}),
                ]
            )

    def test_handles_exc(self, task):
        task_dict = TaskOut.from_orm(task).dict()
        m = process_task.__module__
        with mock.patch(
            f"{m}.TasksApiClient", return_value=mock.MagicMock(spec=TasksApiClient)
        ) as mock_client_class, mock.patch(f"{m}.gevent") as mock_gevent:
            mock_client = mock_client_class.return_value
            mock_client.read_task.side_effect = TasksApiException
            process_task(str(task.task_id))
            mock_gevent.sleep.assert_not_called()
            mock_client.read_task.assert_called_once_with(str(task.task_id))
            assert mock_client.update_task.call_count == 1
            mock_client.update_task.assert_has_calls([call(str(task.task_id), {"status": Task.Status.ERROR.value})])
