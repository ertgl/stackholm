import asyncio
from contextvars import ContextVar
import multiprocessing
from typing import (
    Coroutine,
    List,
)
import unittest

import stackholm


STATE_VAR_1: ContextVar[stackholm.State] = ContextVar('STATE_VAR_1')


class ContextVarStorageTestCase(unittest.TestCase):

    def test_isolation(self) -> None:
        storage = stackholm.ContextVarStorage(STATE_VAR_1)
        context_class = storage.create_context_class()

        async def test_tasks() -> None:

            async def test_sub_cpu_context() -> None:
                sub_context_counter_limit = 1000
                with context_class():
                    for _ in range(sub_context_counter_limit):
                        sub_context_counter = context_class.get_checkpoint_value('counter', 0)
                        context_class.set_checkpoint_value('counter', sub_context_counter + 1)
                    self.assertEqual(context_class.get_checkpoint_value('counter'), sub_context_counter_limit)

            tasks: List[Coroutine] = []
            tasks_count = min(max(multiprocessing.cpu_count(), 8), 64)

            with context_class():
                for _ in range(tasks_count):
                    tasks.append(test_sub_cpu_context())
                await asyncio.gather(*tasks)

        asyncio.run(test_tasks())
