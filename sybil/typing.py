from typing import Callable, TYPE_CHECKING, Iterable, TypeVar, Optional

if TYPE_CHECKING:
    from .document import Document
    from .example import Example
    from .region import Region, LexedRegion


Parsed = TypeVar('Parsed')
Evaluator = Callable[['Example'], Optional[str]]
Lexer = Callable[['Document'], Iterable['LexedRegion']]
Parser = Callable[['Document'], Iterable['Region']]
