from os import chdir, getcwd
from shutil import rmtree
from tempfile import mkdtemp
import pytest
from sybil import Sybil, DocTestParser, CodeBlockParser

@pytest.fixture(scope="module")
def tempdir():
    # there are better ways to do temp directories, but it's a simple example:
    path = mkdtemp()
    cwd = getcwd()
    try:
        chdir(path)
        yield path
    finally:
        chdir(cwd)
        rmtree(path)

pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(),
        CodeBlockParser(future_imports=['print_function']),
    ],
    pattern='*.rst',
    fixtures=['tempdir']
).pytest()
