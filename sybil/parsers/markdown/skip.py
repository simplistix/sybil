from ..abstract import AbstractSkipParser
from ..markdown.lexers import DirectiveInHTMLCommentLexer


class SkipParser(AbstractSkipParser):
    """
    A :any:`Parser` for :ref:`skip <markdown-skip-parser>` instructions.
    """

    def __init__(self, directive: str = 'skip') -> None:
        super().__init__([
            DirectiveInHTMLCommentLexer(directive=directive),
        ])
