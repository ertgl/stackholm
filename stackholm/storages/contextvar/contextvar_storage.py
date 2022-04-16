from contextvars import ContextVar
from typing import Any

from stackholm.state import State
from stackholm.storages.optimized_list.optimized_list_storage import (
    OptimizedListStorage,
)


__all__ = (
    'ContextVarStorage',
)


class ContextVarStorage(OptimizedListStorage):

    _context_var: ContextVar[State]

    def __init__(
        self,
        context_var: ContextVar[State],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._context_var = context_var
        super(ContextVarStorage, self).__init__(*args, **kwargs)

    def get_state(self) -> State:
        return self._context_var.get()

    def set_state(
        self,
        state: State,
    ) -> None:
        self._context_var.set(state)
