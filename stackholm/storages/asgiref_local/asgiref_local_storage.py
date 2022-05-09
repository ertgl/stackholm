from typing import (
    Any,
    Optional,
)

from asgiref.local import Local as _ASGIRefLocal

from stackholm.state import State
from stackholm.storages.optimized_list.optimized_list_storage import (
    OptimizedListStorage,
)


__all__ = (
    'ASGIRefLocal',
    'ASGIRefLocalStorage',
)


class ASGIRefLocal(_ASGIRefLocal):

    state: State

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super(ASGIRefLocal, self).__init__()


class ASGIRefLocalStorage(OptimizedListStorage):

    _local: ASGIRefLocal

    def __init__(
        self,
        *args: Any,
        local: Optional[ASGIRefLocal] = None,
        thread_critical: bool = False,
        **kwargs: Any,
    ) -> None:
        self._local = local or ASGIRefLocal(thread_critical=thread_critical)
        super(ASGIRefLocalStorage, self).__init__(*args, **kwargs)

    def get_state(self) -> State:
        if not hasattr(self._local, 'state'):
            self.set_state(self.__class__.get_state_class()())
        return self._local.state

    def set_state(
        self,
        state: State,
    ) -> None:
        self._local.state = state
