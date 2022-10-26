import re
from typing import Dict

from sybil.parsers.abstract.lexers import BlockLexer

CODEBLOCK_START_TEMPLATE = r"^(?P<prefix>[ \t]*)```(?P<language>{language})$\n"
CODEBLOCK_END_TEMPLATE = r"(?<=\n){prefix}```\n"


class FencedCodeBlockLexer(BlockLexer):
    """
    A :class:`~sybil.parsers.abstract.lexers.BlockLexer` for Markdown fenced code blocks.

    The following lexemes are extracted:

    - ``language`` as a  :class:`str`.
    - ``source`` as a :class:`~sybil.Lexeme`.


    :param language:
        a :class:`str` containing a regular expression pattern to match language names.

    :param mapping:
        If provided, this is used to rename lexemes from the keys in the mapping to their
        values. Only mapped lexemes will be returned in any :class:`~sybil.LexedRegion` objects.

    """

    def __init__(self, language: str, mapping: Dict[str, str] = None):
        super().__init__(
            start_pattern=re.compile(CODEBLOCK_START_TEMPLATE.format(language=language)),
            end_pattern_template=CODEBLOCK_END_TEMPLATE,
            mapping=mapping,
        )
        self.start_pattern = re.compile(
            CODEBLOCK_START_TEMPLATE.format(language=language),
            re.MULTILINE
        )


DIRECTIVE_START_TEMPLATE = (
    r"^(?P<prefix>[ \t]*)```\{{(?P<directive>{directive})}} ?(?P<arguments>{arguments})$\n"
    r"(\1---\n(.+\n)*\1---\n)?"
)


class DirectiveLexer(BlockLexer):
    """
    A :class:`~sybil.parsers.abstract.lexers.BlockLexer` for MyST directives such as:

    .. code-block:: markdown

        ```{directivename} arguments
        ---
        key1: val1
        key2: val2
        ---
        This is
        directive content
        ```

    The following lexemes are extracted:

    - ``directive`` as a  :class:`str`.
    - ``arguments`` as a :class:`str`.
    - ``source`` as a :class:`~sybil.Lexeme`.

    :param directive:
        a :class:`str` containing a regular expression pattern to match directive names.

    :param arguments:
        a :class:`str` containing a regular expression pattern to match directive arguments.

    :param mapping:
        If provided, this is used to rename lexemes from the keys in the mapping to their
        values. Only mapped lexemes will be returned in any :class:`~sybil.LexedRegion` objects.

    """

    def __init__(self, directive: str, arguments: str = '', mapping: Dict[str, str] = None):
        super().__init__(
            start_pattern=re.compile(
                DIRECTIVE_START_TEMPLATE.format(directive=directive, arguments=arguments),
                re.MULTILINE
            ),
            end_pattern_template=CODEBLOCK_END_TEMPLATE,
            mapping=mapping,
        )


DIRECTIVE_IN_PERCENT_COMMENT_START = (
    r"^(?P<prefix>[ \t]*%)[ \t]*(?P<directive>{directive}):[ \t]*(?P<arguments>{arguments})$\n"
)
DIRECTIVE_IN_PERCENT_COMMENT_END = '(?<=\n)(?!{prefix})'


class DirectiveInPercentCommentLexer(BlockLexer):
    """
    A :class:`~sybil.parsers.abstract.lexers.BlockLexer` for faux MyST directives in
    %-style Markdown comments such as:

    .. code-block:: markdown

        ; not-really-a-directive: some-argument
        ;
        ;     Source here...

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

    def __init__(self, directive: str, arguments: str = '', mapping: Dict[str, str] = None):
        super().__init__(
            start_pattern=re.compile(
                DIRECTIVE_IN_PERCENT_COMMENT_START.format(directive=directive, arguments=arguments),
                re.MULTILINE
            ),
            end_pattern_template=DIRECTIVE_IN_PERCENT_COMMENT_END,
            mapping=mapping,
        )


DIRECTIVE_IN_HTML_COMMENT_START = (
    r"^(?P<prefix>[ \t]*)<!---[ \t]*(?P<directive>{directive}):[ \t]*(?P<arguments>{arguments})$\n"
)
DIRECTIVE_IN_HTML_COMMENT_END = '(?<=\n){prefix}--->'


class DirectiveInHTMLCommentLexer(BlockLexer):
    """
    A :class:`~sybil.parsers.abstract.lexers.BlockLexer` for faux MyST directives in
    HTML-style Markdown comments such as:

    .. code-block:: markdown

        <!--- not-really-a-directive: some-argument

            Source here...

        --->

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

    def __init__(self, directive: str, arguments: str = '', mapping: Dict[str, str] = None):
        super().__init__(
            start_pattern=re.compile(
                DIRECTIVE_IN_HTML_COMMENT_START.format(directive=directive, arguments=arguments),
                re.MULTILINE
            ),
            end_pattern_template=DIRECTIVE_IN_HTML_COMMENT_END,
            mapping=mapping,
        )
