
try:
    import asgiref  # noqa
    IS_ASGIREF_INSTALLED = True
except ImportError:
    IS_ASGIREF_INSTALLED = False


__all__ = (
    'IS_ASGIREF_INSTALLED',
)
