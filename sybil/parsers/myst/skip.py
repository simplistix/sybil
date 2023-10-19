from ..abstract import AbstractSkipParser
from .lexers import DirectiveInPercentCommentLexer, DirectiveInHTMLCommentLexer


class SkipParser(AbstractSkipParser):
    """
    A :any:`Parser` for :ref:`skip <myst-skip-parser>` instructions.
    """

    def __init__(self):
        super().__init__([
            DirectiveInPercentCommentLexer('skip'),
            DirectiveInHTMLCommentLexer('skip'),
        ])
