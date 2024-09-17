from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Optional, Any, Dict

if TYPE_CHECKING:
    import sybil


#: The signature for an :term:`evaluator`.
Evaluator = Callable[['sybil.Example'], Optional[str]]

#: The signature for a :term:`lexer`.
#: Lexers must not set :attr:`~sybil.Region.parsed` or :attr:`~sybil.Region.evaluator`
#: on the :class:`~sybil.Region` instances they return.
Lexer = Callable[['sybil.Document'], Iterable['sybil.Region']]

#: The signature for a :term:`parser`.
Parser = Callable[['sybil.Document'], Iterable['sybil.Region']]

# This could likely be a TypedDict.
#: Mappings used to store lexemes for a :class:`~sybil.Region`.
LexemeMapping = Dict[str, Any]
