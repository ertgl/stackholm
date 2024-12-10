# Stackholm

Stackholm is a stack-based context management library, designed to
provide efficient and flexible context handling in Python applications.

This project is particularly useful for managing flat/nested contexts and
ensuring that resources are properly handled and released, whether in a
single-threaded, multi-threaded or asynchronous environment.

[ASGI](https://asgi.readthedocs.io/) applications can also benefit from
stackholm, as it provides an integration with the ASGI reference local storage.

## Why?

In some applications, managing contexts efficiently is crucial for performance
and resource management.

Let's consider a simple example of tracking the changes made to a data object.
The most straightforward way to implement this is to use a key-value mapping to
store the initial state of the object, and then update the object with the new
values, and finally, compare the two states to determine the changes.

However, this approach has some limitations. Post-processing the data to
determine the changes is computationally expensive. This is multiplied when
dealing with post-save signals that upserts another data that must be tracked
as well.

The problem becomes more complex when multiple actors are involved in making
changes to the data. In such cases, it is essential to ensure that each actor's
changes are isolated and properly managed. Without proper context management,
the time complexity that the runtime spends on managing the contexts can
increase exponentially. This can lead to performance bottlenecks.

## How?

Stackholm uses a stack-based approach to manage contexts. Each context is
pushed onto a stack, and when the context is exited, it is popped from the
stack. This ensures that contexts are managed in a last-in first-out (LIFO)
manner.

So, let's consider the same example of tracking changes to a data object.
We would still use the mapping for storing the state of the object, but now,
we would fill the mapping on-the-fly, as the changes are made to the object.
And, as the states are ready, we would write them to the database.

This approach is more efficient because it eliminates the need for a long-lived
post-processing the data to determine the changes. Instead, the changes are
tracked in real-time, as the data is being modified.

See also project [revy](https://github.com/ertgl/revy), which is built on top
of stackholm for that specific use case. It is a revision control system
designed to work with [Django](https://www.djangoproject.com/) applications,
by offering simplicity without compromising the performance,
even in the presence of nested transactions.

## Installation

Stackholm is available on [PyPI](https://pypi.org/project/stackholm/), and can
be installed using pip:

```bash
pip install stackholm
```

## Usage

Stackholm provides a simple API for managing contexts. The `Context` class
provides a context manager that can be used with the `with` statement.

### Single-threaded Environment

Here is a simple example of using stackholm to manage contexts in a single
threaded environment:

```python
import stackholm

# Create a context class, using the default list storage.
storage = stackholm.OptimizedListStorage()
Context = storage.create_context_class()

# Create a context/checkpoint.
with Context():
    # Set a checkpoint value.
    Context.set_checkpoint_value('a', 1)
    # Prints: 1
    print(Context.get_checkpoint_value('a'))

    # Create another context/checkpoint.
    with Context():
        # Prints: 1
        print(Context.get_checkpoint_value('a'))
        # Mutates the value of 'a', only in the current context.
        Context.set_checkpoint_value('a', 2)
        # Prints: 2
        print(Context.get_checkpoint_value('a'))

    # Again, prints: 1
    print(Context.get_checkpoint_value('a'))

# Raises `stackholm.NoContextIsActive` exception.
Context.get_checkpoint_value('a')
```

### Multi-threaded Environment

The `ThreadLocalStorage` class provides a thread-safe storage for contexts.
It uses the built-in `threading.local` class under the hood, to store contexts
in a thread-safe manner.

```python
import stackholm

# Create a context class, using the thread-local storage.
storage = stackholm.ThreadLocalStorage()
Context = storage.create_context_class()
```

### Asynchronous Environment

The `ContextVarStorage` class provides a storage for contexts that can be used
with the built-in `contextvars` module. This is particularly useful for
asynchronous applications, where the context is shared across multiple
coroutines.

```python
from contextvars import ContextVar

import stackholm

# Create a context variable.
# See: https://docs.python.org/3/library/contextvars.html#asyncio-support
STORAGE_STATE_VAR: ContextVar[stackholm.State] = ContextVar('STORAGE_STATE_VAR')

storage = stackholm.ContextVarStorage(STORAGE_STATE_VAR)
context_class = storage.create_context_class()
```

### ASGI Environment

For ASGI applications, stackholm provides an integration with the ASGI reference
local storage, through the `ASGIRefLocalStorage` class. This is particularly
useful for managing contexts in ASGI request/response cycles, that Django and
other ASGI frameworks use.

```python
import stackholm

# Create a context class, using the ASGI reference local storage.
storage = stackholm.ASGIRefLocalStorage()
context_class = storage.create_context_class()
```

## License

Stackholm is licensed under the
[MIT License](https://opensource.org/license/mit).

See the [LICENSE](LICENSE) file for more details.
