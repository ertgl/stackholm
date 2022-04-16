from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from stackholm.context import Context


__all__ = (
    'ContextIsNotActive',
    'NoContextIsActive',
)


class ContextIsNotActive(Exception):

    def __init__(
        self,
        context: 'Context',
        message: str = 'Context is not active.',
    ) -> None:
        super(ContextIsNotActive, self).__init__(message)
        self.context = context


class NoContextIsActive(Exception):

    def __init__(
        self,
        message: str = 'No context is active.',
    ) -> None:
        super(NoContextIsActive, self).__init__(message)
