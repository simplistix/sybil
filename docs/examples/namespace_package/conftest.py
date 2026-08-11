from sybil import Sybil
from sybil.document import NamespacePackageDocument
from sybil.parsers.rest import DocTestParser

pytest_collect_file = Sybil(
    parsers=[DocTestParser()],
    patterns=['*.py'],
    document_types={'.py': NamespacePackageDocument},
).pytest()
