import asyncio
import multiprocessing
from typing import (
    Coroutine,
    List,
)
import unittest


try:
    import asgiref.sync  # noqa
    IS_ASGIREF_INSTALLED = True
except ImportError:
    IS_ASGIREF_INSTALLED = False

import stackholm


if IS_ASGIREF_INSTALLED:

    class ASGIRefLocalStorageTestCase(unittest.TestCase):

        def test_isolation(self) -> None:
            storage = stackholm.ASGIRefLocalStorage()
            context_class = storage.create_context_class()

            async def test_tasks() -> None:

                @asgiref.sync.sync_to_async
                def test_sub_context() -> None:
                    thread_local_counter_limit = 1000
                    with context_class():
                        for _ in range(thread_local_counter_limit):
                            thread_local_counter = context_class.get_checkpoint_value('counter', 0)
                            context_class.set_checkpoint_value('counter', thread_local_counter + 1)
                        self.assertEqual(context_class.get_checkpoint_value('counter'), thread_local_counter_limit)

                tasks: List[Coroutine] = []
                tasks_count = min(max(multiprocessing.cpu_count(), 8), 64)

                with context_class():
                    for _ in range(tasks_count):
                        tasks.append(test_sub_context())
                    await asyncio.gather(*tasks)

            asyncio.run(test_tasks())
