import threading
from typing import (
    Any,
    Optional,
)

from stackholm.state import State
from stackholm.storages.optimized_list.optimized_list_storage import (
    OptimizedListStorage,
)


__all__ = (
    'ThreadLocal',
    'ThreadLocalStorage',
)


class ThreadLocal(threading.local):

    state: State

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super(ThreadLocal, self).__init__()


class ThreadLocalStorage(OptimizedListStorage):

    _local: ThreadLocal

    def __init__(
        self,
        *args: Any,
        local: Optional[ThreadLocal] = None,
        **kwargs: Any,
    ) -> None:
        self._local = local or ThreadLocal()
        super(ThreadLocalStorage, self).__init__(*args, **kwargs)

    def get_state(self) -> State:
        if not hasattr(self._local, 'state'):
            self.set_state(self.__class__.get_state_class()())
        return self._local.state

    def set_state(
        self,
        state: State,
    ) -> None:
        self._local.state = state
