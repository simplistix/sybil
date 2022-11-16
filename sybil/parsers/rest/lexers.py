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
    # This is the pattern used for invisible code blocks and the like.
    delimiter = ':'
