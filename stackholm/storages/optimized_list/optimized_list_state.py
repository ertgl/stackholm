from contextlib import suppress
from typing import (
    Dict,
    List,
    Optional,
)

from stackholm.context import Context
from stackholm.state import State


__all__ = (
    'OptimizedListState',
)


class OptimizedListState(State):

    context_sequence: int

    contexts: List[Context]

    checkpoint_sequences: Dict[str, int]

    checkpoint_indexes: Dict[str, List[int]]

    checkpoint_optimization_mapping: Dict[str, Dict[int, int]]

    def __init__(self) -> None:
        self.context_sequence = -1
        self.contexts = []
        self.checkpoint_sequences = {}
        self.checkpoint_indexes = {}
        self.checkpoint_optimization_mapping = {}

    def push_context(
        self,
        context: Context,
    ) -> int:
        self.context_sequence += 1
        self.contexts.append(context)
        return self.context_sequence

    def pop_context(
        self,
        index: int = -1,
    ) -> Optional[Context]:
        self.context_sequence -= 1
        with suppress(IndexError):
            return self.contexts.pop(index)
        return None

    def get_last_context(self) -> Optional[Context]:
        with suppress(IndexError):
            return self.contexts[-1]
        return None

    def add_checkpoint(
        self,
        key: str,
        context_index: int,
    ) -> None:
        if key not in self.checkpoint_sequences:
            self.checkpoint_sequences[key] = -1
        if key not in self.checkpoint_optimization_mapping:
            self.checkpoint_optimization_mapping[key] = {}
        if key not in self.checkpoint_indexes:
            self.checkpoint_indexes[key] = []
        self.checkpoint_sequences[key] += 1
        checkpoint_index = self.checkpoint_sequences[key]
        self.checkpoint_optimization_mapping[key][context_index] = checkpoint_index
        self.checkpoint_indexes[key].append(context_index)

    def remove_checkpoint(
        self,
        key: str,
        context_index: int,
    ) -> None:
        checkpoint_index: Optional[int] = None
        if key in self.checkpoint_optimization_mapping:
            checkpoint_index = self.checkpoint_optimization_mapping[key].pop(context_index, None)
            if not self.checkpoint_optimization_mapping[key]:
                self.checkpoint_optimization_mapping.pop(key, None)
        if key in self.checkpoint_indexes and checkpoint_index is None:
            with suppress(ValueError):
                checkpoint_index = self.checkpoint_indexes[key].index(context_index)
        if checkpoint_index is not None:
            if key in self.checkpoint_sequences:
                self.checkpoint_sequences[key] -= 1
            if self.checkpoint_sequences[key] < 0:
                self.checkpoint_sequences.pop(key, None)
            self.checkpoint_indexes[key].pop(checkpoint_index)
            if not self.checkpoint_indexes[key]:
                self.checkpoint_indexes.pop(key, None)

    def get_nearest_checkpoint(
        self,
        key: str,
    ) -> Optional[Context]:
        with suppress(KeyError, IndexError):
            return self.contexts[self.checkpoint_indexes[key][-1]]
        return None
