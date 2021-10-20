import importlib
import sys
from contextlib import contextmanager


@contextmanager
def import_cleanup():
    """
    Clean up the results of importing modules, including the modification
    of :attr:`sys.path` necessary to do so.
    """
    modules = set(sys.modules)
    path = sys.path.copy()
    yield
    for added_module in set(sys.modules) - modules:
        sys.modules.pop(added_module)
    sys.path[:] = path
    importlib.invalidate_caches()
