from typing import (
    Any,
    cast,
)

from stackholm.state import State
from stackholm.storage import Storage


__all__ = (
    'OptimizedListStorage',
)


class OptimizedListStorage(Storage):

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.set_state(self.__class__.get_state_class()())

    def get_state(self) -> State:
        return cast(State, getattr(self, '_state'))

    def set_state(
        self,
        state: State,
    ) -> None:
        setattr(self, '_state', state)
