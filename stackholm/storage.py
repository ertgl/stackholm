import abc
from typing import (
    Any,
    Dict,
    Optional,
    Tuple,
    Type,
    TypeVar,
    overload,
)

from stackholm.context import Context
from stackholm.state import State


__all__ = (
    'Storage',
)


CONTEXT_T_co = TypeVar('CONTEXT_T_co', bound=Context, covariant=True)


class Storage(
    metaclass=abc.ABCMeta,
):

    @classmethod
    def get_base_context_class(cls) -> Type[Context]:
        return Context

    @classmethod
    def get_state_class(cls) -> Type[State]:
        from stackholm.storages.optimized_list.optimized_list_state import (
            OptimizedListState,
        )
        return OptimizedListState

    @overload
    def create_context_class(
        self,
        name: Optional[str] = None,
        bases: Optional[Tuple[Type, ...]] = None,
        namespace: Optional[Dict[str, Any]] = None,
    ) -> Type[Context]:
        ...

    @overload
    def create_context_class(
        self,
        name: Optional[str] = None,
        base: Type[CONTEXT_T_co] = None,
        bases: Optional[Tuple[Type, ...]] = None,
        namespace: Optional[Dict[str, Any]] = None,
    ) -> Type[CONTEXT_T_co]:
        ...

    def create_context_class(
        self,
        name=None,
        base=None,
        bases=None,
        namespace=None,
    ):
        name = name or 'Context'
        base = base if base is not None else self.__class__.get_base_context_class()
        assert issubclass(base, Context), 'base class must be a subclass of stackholm.Context'  # noqa
        bases = (base,) + (bases or ())
        namespace = namespace or {}
        namespace['_storage'] = self
        context_class = type(name, bases, namespace)
        return context_class

    @abc.abstractmethod
    def get_state(self) -> State:
        raise NotImplementedError()

    @abc.abstractmethod
    def set_state(
        self,
        state: State,
    ) -> None:
        raise NotImplementedError()

    @property
    def state(self) -> State:
        return self.get_state()

    def push_context(
        self,
        context: Context,
    ) -> int:
        return self.state.push_context(context)

    def pop_context(
        self,
        index: int = -1,
    ) -> Optional[Context]:
        return self.state.pop_context(index)

    def get_last_context(self) -> Optional[Context]:
        return self.state.get_last_context()

    def add_checkpoint(
        self,
        key: str,
        context_index: int,
    ) -> None:
        self.state.add_checkpoint(key, context_index)

    def remove_checkpoint(
        self,
        key: str,
        context_index: int,
    ) -> None:
        self.state.remove_checkpoint(key, context_index)

    def get_nearest_checkpoint(
        self,
        key: str,
    ) -> Optional[Context]:
        return self.state.get_nearest_checkpoint(key)
