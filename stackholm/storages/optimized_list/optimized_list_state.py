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
        partition_key: str,
        context_index: int,
    ) -> None:
        if partition_key not in self.checkpoint_sequences:
            self.checkpoint_sequences[partition_key] = -1
        if partition_key not in self.checkpoint_optimization_mapping:
            self.checkpoint_optimization_mapping[partition_key] = {}
        if partition_key not in self.checkpoint_indexes:
            self.checkpoint_indexes[partition_key] = []
        self.checkpoint_sequences[partition_key] += 1
        checkpoint_index = self.checkpoint_sequences[partition_key]
        self.checkpoint_optimization_mapping[partition_key][context_index] = checkpoint_index
        self.checkpoint_indexes[partition_key].append(context_index)

    def remove_checkpoint(
        self,
        partition_key: str,
        context_index: int,
    ) -> None:
        checkpoint_index: Optional[int] = None
        if partition_key in self.checkpoint_optimization_mapping:
            checkpoint_index = self.checkpoint_optimization_mapping[partition_key].pop(context_index, None)
            if not self.checkpoint_optimization_mapping[partition_key]:
                self.checkpoint_optimization_mapping.pop(partition_key, None)
        if partition_key in self.checkpoint_indexes and checkpoint_index is None:
            with suppress(ValueError):
                checkpoint_index = self.checkpoint_indexes[partition_key].index(context_index)
        if checkpoint_index is not None:
            if partition_key in self.checkpoint_sequences:
                self.checkpoint_sequences[partition_key] -= 1
            if self.checkpoint_sequences[partition_key] < 0:
                self.checkpoint_sequences.pop(partition_key, None)
            self.checkpoint_indexes[partition_key].pop(checkpoint_index)
            if not self.checkpoint_indexes[partition_key]:
                self.checkpoint_indexes.pop(partition_key, None)

    def get_nearest_checkpoint(
        self,
        partition_key: str,
    ) -> Optional[Context]:
        with suppress(KeyError, IndexError):
            return self.contexts[self.checkpoint_indexes[partition_key][-1]]
        return None
