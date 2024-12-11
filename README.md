# Stackholm

Stackholm is a stack-based context management library designed to
provide efficient and flexible context handling in Python applications.

This project is particularly useful for managing flat/nested contexts and
ensuring that resources are properly handled and released, whether in a
single-threaded, multi-threaded, or asynchronous environment.

[ASGI](https://asgi.readthedocs.io/) applications can also benefit from
stackholm, as it provides an integration with the ASGI reference local storage.

## Why?

In some applications, managing contexts efficiently is crucial for performance
and resource management.

Let's consider a simple example of tracking the changes made to a data object.
The most straightforward way to implement this is to use a key-value mapping to
store the initial state of the object, then update the object with the new
values, and finally compare the two states to determine the changes.

However, this approach has some limitations. Post-processing the data to
determine the changes is computationally expensive. This is multiplied when
dealing with post-save signals that inserts/updates another data that must be
tracked as well.

To demonstrate the problem, consider the following pseudo example of updating a
record in a Django application:

```python
from django.db import transaction


@transaction.atomic
def update_record_view(request, pk):
    # Mandatory hidden loop.
    record = Record.objects.get(pk)
    # Optional hidden loop.
    initial_state = dict(record)
    # User (actor) is updating the record.
    # Mandatory hidden loop.
    form = RecordForm(request.POST, instance=record)
    # Mandatory hidden loop.
    record = form.save()
    # Store the new state of the record.
    # Optional hidden loop.
    new_state = dict(record)
    # Determine the changes.
    # Optional hidden loop.
    attribute_deltas = generate_deltas(initial_state, new_state)
    # Save the changes to the database.
    # Mandatory hidden loop.
    save_deltas(request.user, attribute_deltas)
```

There are too many hidden loops in the above example; some of them are
mandatory, while others are optional. Before eliminating the optional ones,
let's consider the problem of multiple actors, for the sake of completeness.

The problem becomes even more complex when multiple actors are involved in
making changes to the data in the same transaction. In such cases, it is
essential to ensure that each actor's changes are isolated and properly
managed.

Let's demonstrate the multiple actors problem. Think of a Django application
that uses signals for validating and normalizing a record before saving it to
the database. Assume also that we want to keep the information of what user
exactly changed on the record, and why there are also changes unexpected by the
user, caused by the system.

```python
from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import pre_save


# This code-block is executed in the same database transaction with the caller.
@receiver(pre_save, sender=Record)
def on_record_save(record):
    # Store the initial state of the record.
    # Optional hidden loop.
    initial_state = dict(record)
    # Auto-correction.
    if record.some_field > MAX_LIMIT:
        # System (actor) is updating the record.
        record.some_field = MAX_LIMIT
        # Imagine that the system also creates another record here,
        # due to a business rule. And, this record must be tracked as well.
        # Mandatory hidden loop.
    # Store new state of the record.
    new_state = dict(record)
    # Determine the changes.
    # Optional hidden loop.
    attribute_deltas = generate_deltas(initial_state, new_state)
    # Save the changes to the database.
    # Mandatory hidden loop.
    save_deltas(SYSTEM, attribute_deltas)

@transaction.atomic
def update_record_view(request):
    # Mandatory hidden loop.
    record = Record.objects.get(pk)
    # Optional hidden loop.
    initial_state = dict(record)
    # User (actor) is updating the record.
    # Mandatory hidden loop.
    form = RecordForm(request.POST, instance=record)
    # Mandatory hidden loop.
    record = form.save()
    # Store the new state of the record.
    # Optional hidden loop.
    new_state = dict(record)
    # Determine the changes.
    # Optional hidden loop.
    attribute_deltas = generate_deltas(initial_state, new_state)
    # Save the changes to the database.
    # Mandatory hidden loop.
    save_deltas(request.user, attribute_deltas)
```

In the above example, the `on_record_save` signal handler is executed in the
same database transaction with the `update_record_view` view. The signal
handler is responsible for auto-correcting the record, and creating another
record based on a business rule. The changes made by the system must be
tracked as well, along with the changes made by the user.

The problem with the above example is that there are too many hidden loops
that can be eliminated by restructuring the code to use an iterative approach.
This idea shares the same dynamics with the
[generator](https://en.wikipedia.org/wiki/Generator_(computer_programming))
concept in computer science.

### Conclusion

Without proper context management, the time that the runtime spends on managing
the contexts can increase exponentially. This can lead to performance
bottlenecks, e.g. causing users who submit forms to wait for a while to see the
result of their actions.

## How?

Stackholm uses a stack-based approach to manage contexts. Each context is
pushed onto a stack, and when the context is exited, it is popped from the
stack. This ensures that contexts are managed in a last-in first-out (LIFO)
manner.

So, let's consider the same example of tracking changes to a data object.
We would still use the mapping for storing the state of the object, but now,
we would fill the mapping on-the-fly as the changes are made to the object.
And, as the states are ready, we would write them to the database.

This approach is more efficient because it eliminates the need for a long-lived
post-process of the data to determine the changes. Instead, the changes are
tracked in real-time as the data is being modified.

See also project [revy](https://github.com/ertgl/revy), which is built on top
of stackholm for that specific use case. It is a revision control system
designed to work with [Django](https://www.djangoproject.com/) applications,
by offering simplicity without compromising performance,
even in the presence of nested transactions.

So, with a solution that uses stackholm, the example above would be re-written
as:

```python
from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import pre_save
# Inherits from stackholm's Context class.
from revy import Context


# This code-block is executed in the same database transaction with the caller.
@receiver(pre_save, sender=Record)
def on_record_save(record):
    # Auto-correction.
    if record.some_field > MAX_LIMIT:
        with Context.via_actor(SYSTEM):
            with Context.via_description('Auto-corrected by the system.'):
                # System (actor) is updating the record.
                record.some_field = MAX_LIMIT
            # Imagine that the system also creates another record here,
            # due to a business rule. And, this record must be tracked as well.
            # Mandatory hidden loop.

@transaction.atomic
def update_record_view(request):
    with Context.via_actor(request.user):
        # Mandatory hidden loop.
        record = Record.objects.get(pk)
        # User (actor) is updating the record.
        # Mandatory hidden loop.
        form = RecordForm(request.POST, instance=record)
        # Mandatory hidden loop.
        record = form.save()
```

To eliminate the optional loops, we could make their execution part of the
object construction and modification process. This way, the changes are tracked
in the existing mandatory loops, and the hidden loops are eliminated.

Since Django models' internal logic cannot be changed by user code, `revy`
patches the necessary parts of Django to make the tracking of changes a part
of the model instances' construction and modification process. And, with the
help of stackholm, it knows which actor is making the changes, and associates
specified descriptions with the changes, while generating the deltas. And then,
it saves the deltas to the database in bulk.

This makes the runtime more lightweight, and increases the performance of the
application. Moreover, it makes the code more readable and maintainable, and
allows increased flexibility in managing contexts.

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
