from typing import Tuple

from stackholm.__version__ import (
    VERSION,
    __version__,
)
from stackholm.context import Context
from stackholm.exceptions import (
    ContextIsNotActive,
    NoContextIsActive,
)
from stackholm.state import State
from stackholm.storage import Storage
from stackholm.storages import (
    ContextVarStorage,
    OptimizedListState,
    OptimizedListStorage,
    ThreadLocal,
    ThreadLocalStorage,
)


from stackholm.storages._discovery import IS_ASGIREF_INSTALLED  # noqa


__all__: Tuple[str, ...] = (
    '__version__',
    'VERSION',
    'Context',
    'NoContextIsActive',
    'ContextIsNotActive',
    'State',
    'Storage',
    'ContextVarStorage',
    'OptimizedListState',
    'OptimizedListStorage',
    'ThreadLocal',
    'ThreadLocalStorage',
)


if IS_ASGIREF_INSTALLED:
    from stackholm.storages import (
        ASGIRefLocal,
        ASGIRefLocalStorage,
    )

    __all__ += (
        'ASGIRefLocal',
        'ASGIRefLocalStorage',
    )
