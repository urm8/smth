from unittest import mock

from tasks import selectors
from tasks.models import Task

sentinel = object()


class TestTasks:
    def test_read_task(self):
        with mock.patch("tasks.selectors.get_object_or_404", return_value=sentinel) as mock_get_object_or_404:
            pk = 1024
            assert selectors.read_task(pk=pk) is sentinel
            mock_get_object_or_404.assert_called_once_with(Task, pk=pk)
