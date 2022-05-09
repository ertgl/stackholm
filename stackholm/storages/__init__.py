from typing import Tuple

from stackholm.storages._discovery import IS_ASGIREF_INSTALLED
from stackholm.storages.contextvar import ContextVarStorage
from stackholm.storages.optimized_list import (
    OptimizedListState,
    OptimizedListStorage,
)
from stackholm.storages.thread_local.thread_local_storage import (
    ThreadLocal,
    ThreadLocalStorage,
)


__all__: Tuple[str, ...] = (
    'ContextVarStorage',
    'OptimizedListState',
    'OptimizedListStorage',
    'ThreadLocal',
    'ThreadLocalStorage',
)


if IS_ASGIREF_INSTALLED:
    from stackholm.storages.asgiref_local.asgiref_local_storage import (
        ASGIRefLocal,
        ASGIRefLocalStorage,
    )

    __all__ += (
        'ASGIRefLocal',
        'ASGIRefLocalStorage',
    )
