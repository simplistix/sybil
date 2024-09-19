from doctest import ELLIPSIS
from pathlib import Path
from typing import Tuple, List

import pytest

from sybil import Sybil
from sybil.parsers.rest import (
    CaptureParser,
    DocTestParser,
    PythonCodeBlockParser,
    SkipParser,
)

pytest_collect_file = Sybil(
    parsers=[
        CaptureParser(),
        DocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
        SkipParser(),
    ],
    patterns=['*.rst', '*.py'],
    excludes=['tests/samples/*', 'tests/*']
).pytest()


def _find_python_files() -> List[Tuple[Path, str]]:
    paths = []
    for path in Path(__file__).parent.rglob('*.py'):
        source = Path(path).read_text()
        paths.append((path, source))
    return paths


@pytest.fixture
def all_python_files():
    return _find_python_files()


def pytest_generate_tests(metafunc):
    files = _find_python_files()
    ids = [str(f[0]) for f in files]
    if "python_file" in metafunc.fixturenames:
        metafunc.parametrize("python_file", files, ids=ids)
