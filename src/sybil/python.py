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


def _container(path: Path) -> Path:
    container = path
    while True:
        container = container.parent
        if not (container / INIT_FILE).exists():
            break
    return container


def _module_name(path: Path, container: Path) -> str:
    relative = path.relative_to(container)
    if relative.name == INIT_FILE:
        parts = tuple(relative.parts)[:-1]
    else:
        parts = tuple(relative.parts)[:-1] + (relative.stem,)
    return '.'.join(parts)


def _find_spec(module: str) -> Optional[ModuleSpec]:
    try:
        return importlib.util.find_spec(module)
    except (ImportError, ValueError):
        # ImportError: a parent isn't importable.
        # ValueError: a parent is in sys.modules but has no __spec__.
        return None


def _resolves_to(module: str, path: Path) -> bool:
    spec = _find_spec(module)
    return spec is not None and spec.origin is not None and Path(spec.origin) == path


def _import(module: str, path: Path) -> ModuleType:
    try:
        return importlib.import_module(module)
    except ImportError as e:
        raise ImportError(
            f'{module!r} not importable from {path} as:\n{type(e).__name__}: {e}'
        ) from None


def import_path(path: Path) -> ModuleType:
    """
    Import the module contained in the file at ``path``.

    The module's dotted name is worked out by walking up from ``path`` until a
    directory without an ``__init__.py`` is found.
    """
    return _import(_module_name(path, _container(path)), path)


def import_namespace_path(path: Path) -> ModuleType:
    """
    Import the module contained in the file at ``path``, allowing for
    :pep:`420` namespace packages.

    Namespace packages have no ``__init__.py``, so the walk up performed by
    :func:`import_path` stops inside them and the dotted name comes out missing
    its leading parts. Where that name isn't importable at all, the walk
    continues upwards looking for a longer one that names this same file.

    Since that only happens once the shorter name has been found unusable, this
    can rescue an import that would otherwise have failed, but can never change
    one that already worked.
    """
    container = _container(path)
    module = _module_name(path, container)
    if module not in sys.modules and _find_spec(module) is None:
        for candidate in container.parents:
            longer = _module_name(path, candidate)
            if _resolves_to(longer, path):
                module = longer
                break
    return _import(module, path)
