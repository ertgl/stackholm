# Stackholm

A
[context manager](https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager)
for storing and retrieving scope-specific values in a stack-based manner.

## Overview

Stackholm is a Python package that provides an API for managing context data.
It allows you to store and retrieve values in a stack-based manner, where
the values are scoped to the current context. The package is designed to be
simple and lightweight, and can be used in a variety of environments.

### Features

- Single-threaded, multi-threaded, asynchronous, and
  [ASGI](https://en.wikipedia.org/wiki/Asynchronous_Server_Gateway_Interface)
  environment support.
- Indexed storage for fast lookups.
- Fallbacks to upper contexts for missing values.
- Scopes are not limited to blocks, and can be nested within functions or
  methods.

## Installation

The package is available on [PyPI](https://pypi.org/project/stackholm/), and can
be installed using pip:

```bash
pip install stackholm
```

## Usage

Stackholm contexts require a storage class for managing the datas in the
scopes. The package provides several storage classes that can be used in
different environments.

See the following sections for the usage examples in different environments.

### Single-threaded Environment

The `OptimizedListStorage` class can be used for single-threaded applications.
This storage class uses indexes for fast lookups.

```python
import stackholm

# Create a context class, using the optimized list storage.
storage = stackholm.OptimizedListStorage()
Context = storage.create_context_class()

# Create a context (checkpoint).
with Context():
    # Set a checkpoint value in the current context.
    Context.set_checkpoint_value("a", 1)

    # Prints: 1
    print(Context.get_checkpoint_value("a"))

    # Create another context/checkpoint nested within the current context.
    with Context() as inner_context:
        # In this scope, the current context is the `inner_context`.

        # The values from upper contexts are accessible,
        # without any copy operation.

        # Prints: 1
        print(Context.get_checkpoint_value("a"))

        # Mutates the value of `"a"`, only for the current context.
        Context.set_checkpoint_value("a", 2)
        
        # Prints: 2
        print(Context.get_checkpoint_value("a"))

    # Back to the previous context.
    # Prints: 1
    print(Context.get_checkpoint_value("a"))

# The context is closed, and the values are no longer accessible.
# Raises `stackholm.NoContextIsActive` exception.
Context.get_checkpoint_value("a")
```

### Multi-threaded Environment

The `ThreadLocalStorage` class can be used for multi-threaded applications.
It uses the built-in `threading.local` class behind the scenes, and it is
an extension of the `OptimizedListStorage` class.

```python
import stackholm

storage = stackholm.ThreadLocalStorage()
Context = storage.create_context_class()
```

For more information on `threading.local`, see the
[official documentation](https://docs.python.org/3/library/threading.html#thread-local-data).

### Asynchronous Environment

The `ContextVarStorage` class can be used for asynchronous applications.
It requires a `ContextVar` instance to be passed to the constructor, which
is used for storing the context data in the corresponding coroutine. The
`ContextVarStorage` class is an extension of the `OptimizedListStorage` class.

```python
from contextvars import ContextVar

import stackholm

# Create a `ContextVar` instance for storing the context data.
STORAGE_STATE_VAR: ContextVar[stackholm.State] = ContextVar("STORAGE_STATE_VAR")

# Pass the `ContextVar` instance to the `ContextVarStorage` constructor.
storage = stackholm.ContextVarStorage(STORAGE_STATE_VAR)
Context = storage.create_context_class()
```

For more information on using `ContextVar` with asynchronous applications, see
the
[official documentation](https://docs.python.org/3/library/contextvars.html#asyncio-support).

### ASGI Environment

The `ASGIRefLocalStorage` class can be used for ASGI applications. It uses
the ASGI reference local storage for storing the context data. The class is
an extension of the `OptimizedListStorage` class.

```python
import stackholm

storage = stackholm.ASGIRefLocalStorage()
Context = storage.create_context_class()
```

## Real-world Examples

For a complete example of using Stackholm in a real-world application, you may
refer to the project [revy](https://github.com/ertgl/revy), which provides a
re-usable [Django](https://www.djangoproject.com/) application for building
revision control systems around the database models. It uses Stackholm for
tracking data changes and the related informations in the contexts.

## License

This project is licensed under the
[MIT License](https://opensource.org/license/mit).

See the [LICENSE](LICENSE) file for more details.
