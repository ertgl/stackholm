import abc
from typing import Optional

from stackholm.context import Context


__all__ = (
    'State',
)


class State(
    metaclass=abc.ABCMeta,
):

    @abc.abstractmethod
    def push_context(
        self,
        context: Context,
    ) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    def pop_context(
        self,
        index: int = -1,
    ) -> Optional[Context]:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_last_context(self) -> Optional[Context]:
        raise NotImplementedError()

    @abc.abstractmethod
    def add_checkpoint(
        self,
        key: str,
        context_index: int,
    ) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def remove_checkpoint(
        self,
        key: str,
        context_index: int,
    ) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_nearest_checkpoint(
        self,
        key: str,
    ) -> Optional[Context]:
        raise NotImplementedError()
