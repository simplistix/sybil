import re
from collections.abc import Iterable
from typing import Optional, Dict, Pattern, Match, List

from sybil import Document, Region, Lexeme
from sybil.parsers.abstract.lexers import BlockLexer, strip_prefix

FENCE = re.compile(r"^(?P<prefix>[ \t]*)(?P<fence>`{3,}|~{3,})", re.MULTILINE)


class RawFencedCodeBlockLexer:
    """
    A :class:`~sybil.typing.Lexer` for Markdown fenced code blocks allowing flexible lexing
    of the whole `info` line along with more complicated prefixes.

    The following lexemes are extracted:

    - ``source`` as a :class:`~sybil.Lexeme`.
    - any other named groups specified in ``info_pattern`` as :class:`strings <str>`.


    :param info_pattern:
        a :class:`re.Pattern` to match the `info` line and any required prefix that follows it.

    :param mapping:
        If provided, this is used to rename lexemes from the keys in the mapping to their
        values. Only mapped lexemes will be returned in any :class:`~sybil.Region` objects.

    """


    def __init__(
            self,
            info_pattern: Pattern[str] = re.compile(r'$\n', re.MULTILINE),
            mapping: Optional[Dict[str, str]] = None,
    ) -> None:
        self.info_pattern = info_pattern
        self.mapping = mapping

    @staticmethod
    def match_closes_existing(current: Match[str], existing: Match[str]) -> bool:
        current_fence = current.group('fence')
        existing_fence = existing.group('fence')
        same_type = current_fence[0] == existing_fence[0]
        okay_length = len(current_fence) >= len(existing_fence)
        same_prefix = len(current.group('prefix')) == len(existing.group('prefix'))
        return same_type and okay_length and same_prefix

    def make_region(
            self, opening: Match[str], document: Document, closing: Optional[Match[str]]
    ) -> Optional[Region]:
        if closing is None:
            content_end = region_end = len(document.text)
        else:
            content_end = closing.start()
            region_end = closing.end()
        content = document.text[opening.end(): content_end]
        info = self.info_pattern.match(content)
        if info is None:
            return None
        lexemes = info.groupdict()
        lexemes['source'] = Lexeme(
            strip_prefix(content[info.end():], opening.group('prefix')),
            offset=len(opening.group(0))+info.end(),
            line_offset=0,
        )
        if self.mapping:
            lexemes = {dest: lexemes[source] for source, dest in self.mapping.items()}
        return Region(opening.start(), region_end, lexemes=lexemes)

    def __call__(self, document: Document) -> Iterable[Region]:
        open_blocks: List[Match[str]] = []
        index = 0
        while True:
            match = FENCE.search(document.text, index)
            if match is None:
                break
            else:
                index = match.end()
            # does this fence close any open block?
            for i in range(len(open_blocks)):
                existing = open_blocks[i]
                if self.match_closes_existing(match, existing):
                    maybe_region = self.make_region(existing, document, match)
                    if maybe_region is not None:
                        yield maybe_region
                    open_blocks = open_blocks[:i]
                    break
            else:
                open_blocks.append(match)
        if open_blocks:
            maybe_region = self.make_region(open_blocks[0], document, closing=None)
            if maybe_region is not None:
                yield maybe_region


class FencedCodeBlockLexer(RawFencedCodeBlockLexer):
    """
    A :class:`~sybil.typing.Lexer` for Markdown fenced code blocks where a language is specified.
    :class:`RawFencedCodeBlockLexer` can be used if the whole `info` line, or a more complicated
    prefix, is required.

    The following lexemes are extracted:

    - ``language`` as a  :class:`str`.
    - ``source`` as a :class:`~sybil.Lexeme`.


    :param language:
        a :class:`str` containing a regular expression pattern to match language names.

    :param mapping:
        If provided, this is used to rename lexemes from the keys in the mapping to their
        values. Only mapped lexemes will be returned in any :class:`~sybil.Region` objects.

    """

    def __init__(self, language: str, mapping: Optional[Dict[str, str]] = None) -> None:
        super().__init__(
            info_pattern=re.compile(f'(?P<language>{language})$\n', re.MULTILINE),
            mapping=mapping,
        )


DIRECTIVE_IN_HTML_COMMENT_START = (
    r"^(?P<prefix>[ \t]*)<!--+\s*(?:;\s*)?(?P<directive>{directive}):?[ \t]"
    r"*(?P<arguments>{arguments})[ \t]*"
    r"(?:$\n|(?=--+>))"
)
DIRECTIVE_IN_HTML_COMMENT_END = '(?:(?<=\n){prefix})?--+>'


class DirectiveInHTMLCommentLexer(BlockLexer):
    """
    A :class:`~sybil.parsers.abstract.lexers.BlockLexer` for faux directives in
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
        Only mapped lexemes will be returned in any :class:`~sybil.Region` objects.
    """

    def __init__(
            self, directive: str, arguments: str = '.*?', mapping: Optional[Dict[str, str]] = None
    ) -> None:
        super().__init__(
            start_pattern=re.compile(
                DIRECTIVE_IN_HTML_COMMENT_START.format(directive=directive, arguments=arguments),
                re.MULTILINE
            ),
            end_pattern_template=DIRECTIVE_IN_HTML_COMMENT_END,
            mapping=mapping,
        )
