import re
from typing import Dict

from sybil.parsers.abstract.lexers import BlockLexer

START_PATTERN_TEMPLATE =(
    r'^(?P<prefix>[ \t]*)\.\.\s*(?P<directive>{directive})'
    r'{delimiter}\s*'
    r'(?P<arguments>[\w-]+\b)?'
    r'(?:\s*\:[\w-]+\:.*\n)*'
    r'(?:\s*\n)*\n'
)

END_PATTERN_TEMPLATE = '(\n\\Z|\n[ \t]{{0,{len_prefix}}}(?=\\S))'


class DirectiveLexer(BlockLexer):
    """
    A :class:`~sybil.parsers.abstract.lexers.BlockLexer` for ReST directives that extracts the
    following lexemes:

    - ``directive`` as a  :class:`str`.
    - ``arguments`` as a :class:`str`.
    - ``source`` as a :class:`~sybil.Lexeme`.

    :param directive:
        a :class:`str` containing a regular expression pattern to match directive names.

    :param arguments:
        a :class:`str` containing a regular expression pattern to match directive arguments.

    :param mapping:
        If provided, this is used to rename lexemes from the keys in the mapping to their values.
        Only mapped lexemes will be returned in any :class:`~sybil.LexedRegion` objects.
    """

    delimiter = '::'

    def __init__(self, directive: str, arguments: str = '', mapping: Dict[str, str] = None):
        """
        A lexer for ReST directives.
        Both ``directive`` and ``arguments`` are regex patterns.
        """
        super().__init__(
            start_pattern=re.compile(
                START_PATTERN_TEMPLATE.format(
                    directive=directive,
                    delimiter=self.delimiter,
                    arguments=arguments
                ),
                re.MULTILINE
            ),
            end_pattern_template=END_PATTERN_TEMPLATE,
            mapping=mapping,
        )


class DirectiveInCommentLexer(DirectiveLexer):
    """
    A :class:`~sybil.parsers.abstract.lexers.BlockLexer` for faux ReST directives in comments
    such as:

    .. code-block:: rest

        .. not-really-a-directive: some-argument

          Source here...

    It extracts the following lexemes:

    - ``directive`` as a  :class:`str`.
    - ``arguments`` as a :class:`str`.
    - ``source`` as a :class:`~sybil.Lexeme`.

    :param directive:
        a :class:`str` containing a regular expression pattern to match directive names.

    :param arguments:
        a :class:`str` containing a regular expression pattern to match directive arguments.

    :param mapping:
        If provided, this is used to rename lexemes from the keys in the mapping to their values.
        Only mapped lexemes will be returned in any :class:`~sybil.LexedRegion` objects.
    """

    # This is the pattern used for invisible code blocks and the like.
    delimiter = ':'
