import pytest
from sybil import Sybil
from sybil.parsers.myst import (
    DocTestDirectiveParser as MarkdownDocTestParser,
    PythonCodeBlockParser as MarkdownPythonCodeBlockParser
)
from sybil.parsers.rest import (
    DocTestParser as ReSTDocTestParser,
    PythonCodeBlockParser as ReSTPythonCodeBlockParser
)


@pytest.fixture(scope='session')
def keep_seed():
    import myproj
    seed = myproj.SEED
    yield
    myproj.SEED = seed

markdown_examples = Sybil(
    parsers=[
        MarkdownDocTestParser(),
        MarkdownPythonCodeBlockParser(),
    ],
    patterns=['*.md'],
    fixtures=['keep_seed']
)

rest_examples = Sybil(
    parsers=[
        ReSTDocTestParser(),
        ReSTPythonCodeBlockParser(),
    ],
    patterns=['*.py'],
    fixtures=['keep_seed']
)


pytest_collect_file = (markdown_examples+rest_examples).pytest()
