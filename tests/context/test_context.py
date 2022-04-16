from typing import cast
import unittest

import stackholm


class ContextTestCase(unittest.TestCase):

    def test_storage(self) -> None:
        storage = stackholm.OptimizedListStorage()
        context_class = storage.create_context_class()
        self.assertIs(context_class._storage, storage)

    def test_init(self) -> None:
        storage = stackholm.OptimizedListStorage()
        context_class = storage.create_context_class()
        context = context_class()
        self.assertIs(context.__class__._storage, storage)

    def test_enter_exit(self) -> None:
        storage = stackholm.OptimizedListStorage()
        state = cast(stackholm.OptimizedListState, storage.state)
        context_class = storage.create_context_class()

        with context_class() as context_1:
            self.assertEqual(state.context_sequence, context_1._index)
            with context_class() as context_2:
                self.assertEqual(state.context_sequence, context_2._index)

    def test_get_current(self) -> None:
        storage = stackholm.OptimizedListStorage()
        context_class = storage.create_context_class()

        self.assertIsNone(context_class.get_current())
        with context_class() as context_1:
            self.assertIs(context_class.get_current(), context_1)

            with context_class() as context_2:
                self.assertIs(context_class.get_current(), context_2)
            self.assertIs(context_class.get_current(), context_1)

        self.assertIsNone(context_class.get_current())

    def test_get_nearest_checkpoint(self) -> None:
        storage = stackholm.OptimizedListStorage()
        context_class = storage.create_context_class()

        with context_class():

            with context_class() as context_1:
                context_class.set_checkpoint_value('a', 1)

                with context_class() as context_2:
                    self.assertIs(context_class.get_nearest_checkpoint('a'), context_1)

                    context_class.set_checkpoint_value('a', 1)
                    self.assertIs(context_class.get_nearest_checkpoint('a'), context_2)

                    with context_class():
                        self.assertIs(context_class.get_nearest_checkpoint('a'), context_2)

                        context_class.pop_checkpoint_value('a')
                        self.assertIs(context_class.get_nearest_checkpoint('a'), context_1)

                        context_class.pop_checkpoint_value('a')
                        self.assertIs(context_class.get_nearest_checkpoint('a'), None)

    def test_get_set_unset_block_value(self) -> None:
        storage = stackholm.OptimizedListStorage()
        context_class = storage.create_context_class()

        with context_class() as context_1:
            context_class.set_checkpoint_value('a', 1)
            self.assertIsNone(context_1.get_block_value('a'))

            context_1.set_block_value('a', 2)
            self.assertEqual(context_1.get_block_value('a'), 2)

            with context_class() as context_2:
                self.assertEqual(context_class.get_checkpoint_value('a'), 1)
                self.assertIsNone(context_2.get_block_value('a'))

    def test_get_set_unset_checkpoint_value(self) -> None:
        storage = stackholm.OptimizedListStorage()
        state = cast(stackholm.OptimizedListState, storage.state)
        context_class = storage.create_context_class()

        with context_class():
            self.assertEqual(len(state.checkpoint_indexes), 0)

            with context_class():
                context_class.set_checkpoint_value('a', 1)
                self.assertEqual(len(state.checkpoint_indexes), 1)

                with context_class():
                    self.assertEqual(context_class.get_checkpoint_value('a'), 1)
                    self.assertEqual(len(state.checkpoint_indexes), 1)

                    context_class.set_checkpoint_value('a', 2)
                    self.assertEqual(context_class.get_checkpoint_value('a'), 2)

                    context_class.pop_checkpoint_value('a')
                    self.assertEqual(context_class.get_checkpoint_value('a'), 1)

            self.assertIsNone(context_class.get_checkpoint_value('a'))
            self.assertEqual(len(state.checkpoint_indexes), 0)

    def test_set_checkpoint_value_before_enter(self) -> None:
        storage = stackholm.OptimizedListStorage()
        context_class = storage.create_context_class()

        context_1 = context_class()
        context_1.checkpoint_data['a'] = 1

        self.assertIsNone(context_class.get_checkpoint_value('a'))

        with context_1:
            self.assertEqual(context_class.get_checkpoint_value('a'), 1)

        self.assertIsNone(context_class.get_checkpoint_value('a'))
