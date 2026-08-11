import importlib
import importlib.util
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Optional

from pathlib import Path


@contextmanager
def import_cleanup() -> Iterator[None]:
    """
    Clean up the results of importing modules, including the modification
    of :data:`sys.path` necessary to do so.
    """
    modules = set(sys.modules)
    path = sys.path.copy()
    yield
    for added_module in set(sys.modules) - modules:
        sys.modules.pop(added_module)
    sys.path[:] = path
    importlib.invalidate_caches()


INIT_FILE = '__init__.py'


def find_container(path: Path) -> Path:
    container = path
    while True:
        container = container.parent
        if not (container / INIT_FILE).exists():
            break
    return container


def module_name(path: Path, container: Path) -> str:
    relative = path.relative_to(container)
    if relative.name == INIT_FILE:
        parts = tuple(relative.parts)[:-1]
    else:
        parts = tuple(relative.parts)[:-1] + (relative.stem,)
    return '.'.join(parts)


def find_spec(module: str) -> Optional[ModuleSpec]:
    try:
        return importlib.util.find_spec(module)
    except (ImportError, ValueError):
        # ImportError: a parent isn't importable.
        # ValueError: a parent is in sys.modules but has no __spec__.
        return None


def import_module_from_path(module: str, path: Path) -> ModuleType:
    try:
        return importlib.import_module(module)
    except ImportError as e:
        raise ImportError(
            f'{module!r} not importable from {path} as:\n{type(e).__name__}: {e}'
        ) from None
