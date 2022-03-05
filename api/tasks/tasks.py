from celery import shared_task


@shared_task(bind=True)
def mocked_task(self, task_id: str) -> None:
    pass
