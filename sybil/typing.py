from typing import Callable, TYPE_CHECKING, Iterable, Optional, Any

if TYPE_CHECKING:
    import sybil


#: The signature for an evaluator. See :ref:`developing-parsers`.
Evaluator = Callable[['sybil.Example'], Optional[str]]

#: The signature for a lexer. See :ref:`developing-parsers`.
Lexer = Callable[['sybil.Document'], Iterable['sybil.LexedRegion']]

#: The signature for a parser. See :ref:`developing-parsers`.
Parser = Callable[['sybil.Document'], Iterable['sybil.Region']]
