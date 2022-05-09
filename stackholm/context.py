from contextlib import ContextDecorator
from types import TracebackType
from typing import (
    Any,
    Dict,
    Optional,
    TYPE_CHECKING,
    Type,
    TypeVar,
    Union,
    overload,
)

from stackholm.exceptions import (
    ContextIsNotActive,
    NoContextIsActive,
)


if TYPE_CHECKING:
    from stackholm.storage import Storage


__all__ = (
    'Context',
)


T = TypeVar('T')

VALUE_T = TypeVar('VALUE_T')


class Context(ContextDecorator):

    _storage: 'Storage'

    _index: Optional[int]

    _block_data: Dict[str, Any]

    _checkpoint_data: Dict[str, Any]

    @classmethod
    def get_current(cls) -> Optional['Context']:
        return cls._storage.get_last_context()

    @classmethod
    def get_nearest_checkpoint(
        cls,
        key: str,
    ) -> Optional['Context']:
        return cls._storage.get_nearest_checkpoint(key)

    @classmethod
    @overload
    def get_checkpoint_value(
        cls,
        key: str,
    ) -> Union[VALUE_T, None]:
        ...

    @classmethod
    @overload
    def get_checkpoint_value(
        cls,
        key: str,
        default: VALUE_T,
    ) -> Union[VALUE_T, T]:
        ...

    @classmethod
    def get_checkpoint_value(
        cls,
        key,
        default=None,
    ):
        context = cls.get_nearest_checkpoint(key)
        if context is None:
            return default
        return context._checkpoint_data.get(key, default)

    @classmethod
    def set_checkpoint_value(
        cls,
        key: str,
        value: Any,
    ) -> None:
        context = cls.get_current()
        if context is None:
            raise NoContextIsActive()
        context._checkpoint_data[key] = value
        cls._storage.add_checkpoint(key, context.index)

    @classmethod
    @overload
    def pop_checkpoint_value(
        cls,
        key: str,
    ) -> Union[VALUE_T, None]:
        ...

    @classmethod
    @overload
    def pop_checkpoint_value(
        cls,
        key: str,
        default: VALUE_T,
    ) -> Union[VALUE_T, T]:
        ...

    @classmethod
    def pop_checkpoint_value(
        cls,
        key,
        default=None,
    ):
        context = cls.get_nearest_checkpoint(key)
        if context is None:
            return default
        cls._storage.remove_checkpoint(key, context.index)
        return context._checkpoint_data.pop(key, default)

    @classmethod
    def reset_checkpoint_value(
        cls,
        key: str,
    ) -> None:
        while cls._storage.get_nearest_checkpoint(key) is not None:
            cls.pop_checkpoint_value(key)

    def __init__(self) -> None:
        self._index = None
        self._block_data = {}
        self._checkpoint_data = {}

    def __enter__(self) -> 'Context':
        return self.activate()

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.deactivate()

    @property
    def storage(self) -> 'Storage':
        storage = getattr(self.__class__, '_storage', None)
        assert storage is not None, 'Context class must be bound to a storage.'  # noqa
        return storage

    @property
    def index(self) -> int:
        if self._index is None:
            raise ContextIsNotActive(self)
        return self._index

    @property
    def is_active(self) -> bool:
        return self._index is not None

    @property
    def block_data(self) -> Dict[str, Any]:
        return self._block_data

    @overload
    def get_block_value(
        self,
        key: str,
    ) -> Union[VALUE_T, None]:
        ...

    @overload
    def get_block_value(
        self,
        key: str,
        default: VALUE_T,
    ) -> Union[VALUE_T, T]:
        ...

    def get_block_value(
        self,
        key,
        default=None,
    ):
        return self._block_data.get(key, default)

    def set_block_value(
        self,
        key: str,
        value: Any,
    ) -> None:
        self._block_data[key] = value

    @overload
    def pop_block_value(
        self,
        key: str,
    ) -> Union[VALUE_T, None]:
        ...

    @overload
    def pop_block_value(
        self,
        key: str,
        default: VALUE_T,
    ) -> Union[VALUE_T, T]:
        ...

    def pop_block_value(
        self,
        key,
        default=None,
    ):
        return self._block_data.pop(key, default)

    @property
    def checkpoint_data(self) -> Dict[str, Any]:
        return self._checkpoint_data

    def activate(self) -> 'Context':
        if self.is_active:
            return self
        self._index = self.storage.push_context(self)
        for key in self._checkpoint_data.keys():
            self.storage.add_checkpoint(key, self.index)
        return self

    def deactivate(self) -> None:
        if not self.is_active:
            return
        for key in self._checkpoint_data.keys():
            self.storage.remove_checkpoint(key, self.index)
        self.storage.pop_context(self.index)
        self._index = None
