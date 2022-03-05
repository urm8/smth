from typing import Generic
from typing import TypeVar

from django.db.models import Model
from factory.django import DjangoModelFactory

M = TypeVar("M", bound=Model)


class BaseFactory(Generic[M], DjangoModelFactory):

    # for some reason _generate typing not helping build/create methods with typings
    @classmethod
    def create(cls, **kwargs) -> M:
        return super().create(**kwargs)

    @classmethod
    def create_batch(cls, size, **kwargs) -> list[M]:
        return super().create_batch(size, **kwargs)

    @classmethod
    def build(cls, **kwargs) -> M:
        return super().build(**kwargs)

    @classmethod
    def build_batch(cls, size, **kwargs) -> list[M]:
        return super().build_batch(size, **kwargs)

    @classmethod
    def _generate(cls, strategy, params) -> M:  # noqa
        return super()._generate(strategy, params)
