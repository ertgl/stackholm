# Stackholm

A
[context manager](https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager)
for managing scope-specific values using a stack-based approach.

## Table of Contents
- [Overview](#overview)
  - [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Single-threaded Environment](#single-threaded-environment)
  - [Multi-threaded Environment](#multi-threaded-environment)
  - [Asynchronous Environment](#asynchronous-environment)
  - [ASGI Environment](#asgi-environment)
- [Real-world Example](#real-world-example)
- [License](#license)

## Overview

Stackholm is a lightweight Python package for handling context data
efficiently. It allows storing and retrieving values in a stack-based manner,
ensuring values remain scoped to their respective contexts.

### Features

- Supports single-threaded, multi-threaded, asynchronous, and
  [ASGI](https://en.wikipedia.org/wiki/Asynchronous_Server_Gateway_Interface)
  environments.
- Indexed storage for fast lookups.
- Zero-copy data sharing across nested contexts.
- Scopes can be nested within functions or methods, beyond block-level
  restrictions.

## Installation

The package is available on [PyPI](https://pypi.org/project/stackholm/), and can
be installed using any compatible package manager such as `pip`:

```bash
pip install stackholm
```

## Usage

Stackholm requires a storage class to manage context data. Different storage
classes are available for various environments.

### Single-threaded Environment

Use `OptimizedListStorage` for single-threaded applications. This class
utilizes indexing for efficient lookups.

```python
import stackholm

# Create a context class using optimized list storage.
storage = stackholm.OptimizedListStorage()
Context = storage.create_context_class()

# Create a context (checkpoint).
with Context():
    # Set a value in the current context.
    Context.set_checkpoint_value("a", 1)

    # Output: 1
    print(Context.get_checkpoint_value("a"))

    # Create another context/checkpoint nested within the current context.
    with Context() as inner_context:
        # In this scope, the current context is the `inner_context`.

        # The values from upper contexts are accessible in the current context.

        # Output: 1
        print(Context.get_checkpoint_value("a"))

        # Mutates the value of `"a"`, only for the current context.
        Context.set_checkpoint_value("a", 2)
        
        # Output: 2
        print(Context.get_checkpoint_value("a"))

    # Back to the previous context.
    # Output: 1
    print(Context.get_checkpoint_value("a"))

# The context is closed, and the values are no longer accessible.
# Raises `stackholm.NoContextIsActive` exception.
Context.get_checkpoint_value("a")
```

### Multi-threaded Environment

Use `ThreadLocalStorage` for multi-threaded applications. It extends
`OptimizedListStorage` and leverages Python’s built-in `threading.local`
class to store and retrieve context data.

```python
import stackholm

storage = stackholm.ThreadLocalStorage()
Context = storage.create_context_class()
```

For more information on `threading.local`, refer to the
[official documentation](https://docs.python.org/3/library/threading.html#thread-local-data).

### Asynchronous Environment

Use `ContextVarStorage` for asynchronous applications. It extends
`OptimizedListStorage` and leverages the built-in
`contextvars.ContextVar` class to store and retrieve context data.

```python
from contextvars import ContextVar

import stackholm

# Create a `ContextVar` instance for storing the context data.
STORAGE_STATE_VAR: ContextVar[stackholm.State] = ContextVar("STORAGE_STATE_VAR")

# Pass the `ContextVar` instance to the `ContextVarStorage` constructor.
storage = stackholm.ContextVarStorage(STORAGE_STATE_VAR)
Context = storage.create_context_class()
```

For more information on using `ContextVar` with asynchronous applications,
refer to the
[official documentation](https://docs.python.org/3/library/contextvars.html#asyncio-support).

### ASGI Environment

Use `ASGIRefLocalStorage` for ASGI applications. It extends
`OptimizedListStorage` and utilizes ASGI reference local storage for storing
and retrieving context data.

```python
import stackholm

storage = stackholm.ASGIRefLocalStorage()
Context = storage.create_context_class()
```

## Real-world Example

Stackholm is used in [revy](https://github.com/ertgl/revy), a
re-usable [Django](https://www.djangoproject.com/) application for
building revision control systems. It tracks data changes and manages
context-related information in a fast and efficient way.

## License

This project is licensed under the
[MIT License](https://opensource.org/license/mit).

See the [LICENSE](LICENSE) file for more details.
