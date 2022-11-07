import re
from typing import Dict

from sybil.parsers.abstract.lexers import BlockLexer

CODEBLOCK_START_TEMPLATE = r"^(?P<prefix>[ \t]*)```(?P<language>{language})$\n"
CODEBLOCK_END_TEMPLATE = r"(?<=\n){prefix}```\n"


class FencedCodeBlockLexer(BlockLexer):

    def __init__(self, language: str, mapping: Dict[str, str] = None):
        """
        A lexer for Markdown fenced code blocks.
        ``language`` is a regex pattern.
        """
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

    def __init__(self, directive: str, arguments: str = '', mapping: Dict[str, str] = None):
        """
        An lexer for MyST directives.
        Both ``directive`` and ``arguments`` are regex patterns.
        """
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

    def __init__(self, directive: str, arguments: str = '', mapping: Dict[str, str] = None):
        """
        An lexer for directives in %-style Markdown comments.
        Both ``directive`` and ``arguments`` are regex patterns.
        """
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

    def __init__(self, directive: str, arguments: str = '', mapping: Dict[str, str] = None):
        """
        An lexer for directives in %-style Markdown comments.
        Both ``directive`` and ``arguments`` are regex patterns.
        """
        super().__init__(
            start_pattern=re.compile(
                DIRECTIVE_IN_HTML_COMMENT_START.format(directive=directive, arguments=arguments),
                re.MULTILINE
            ),
            end_pattern_template=DIRECTIVE_IN_HTML_COMMENT_END,
            mapping=mapping,
        )
