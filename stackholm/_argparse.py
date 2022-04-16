import argparse
from typing import Any

from stackholm.__version__ import __version__


__all__ = (
    'ArgumentParser',
)


class ArgumentParser(argparse.ArgumentParser):

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault('prog', 'stackholm')
        kwargs.setdefault('description', 'Stack based context manager framework.')
        super(ArgumentParser, self).__init__(*args, **kwargs)
        self.add_argument(
            '-v',
            '--version',
            action='version',
            version=f'%(prog)s {__version__}',
        )
