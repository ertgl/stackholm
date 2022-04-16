import multiprocessing
import threading
from typing import List
import unittest

import stackholm


class ThreadLocalStorageTestCase(unittest.TestCase):

    def test_isolation(self) -> None:
        storage = stackholm.ThreadLocalStorage()
        context_class = storage.create_context_class()

        def test_sub_thread() -> None:
            thread_local_counter_limit = 1000
            with context_class():
                for _ in range(thread_local_counter_limit):
                    thread_local_counter = context_class.get_checkpoint_value('counter', 0)
                    context_class.set_checkpoint_value('counter', thread_local_counter + 1)
                self.assertEqual(context_class.get_checkpoint_value('counter'), thread_local_counter_limit)

        threads: List[threading.Thread] = []
        threads_count = min(max(multiprocessing.cpu_count(), 8), 64)

        with context_class():

            for _ in range(threads_count):
                thread = threading.Thread(target=test_sub_thread)
                threads.append(thread)

            for thread in threads:
                counter = context_class.get_checkpoint_value('counter', 0)
                thread.start()
                context_class.set_checkpoint_value('counter', counter + 1)

            for thread in threads:
                thread.join()

            self.assertEqual(context_class.get_checkpoint_value('counter'), threads_count)
