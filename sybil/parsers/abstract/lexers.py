import re
import textwrap
from typing import Dict, Iterable, Pattern

from sybil import Document
from sybil.region import LexedRegion, Lexeme


class BlockLexer:

    def __init__(
            self,
            start_pattern: Pattern,
            end_pattern_template: str,
            mapping: Dict[str, str] = None,
    ):
        self.start_pattern = start_pattern
        self.end_pattern_template = end_pattern_template
        self.mapping = mapping

    def __call__(self, document: Document) -> Iterable[LexedRegion]:
        for start_match in re.finditer(self.start_pattern, document.text):
            source_start = start_match.end()
            lexemes = start_match.groupdict()
            prefix = lexemes.pop('prefix', '')
            end_pattern = re.compile(self.end_pattern_template.format(
                prefix=prefix, len_prefix=len(prefix)
            ))
            end_match = end_pattern.search(document.text, source_start)
            source_end = end_match.start()
            source = document.text[source_start:source_end]
            lines = source.splitlines(keepends=True)
            stripped = ''.join(line[len(prefix):] for line in lines)
            lexemes['source'] = Lexeme(
                textwrap.dedent(stripped),
                offset=source_start-start_match.start(),
                line_offset=start_match.group(0).count('\n')-1
            )
            if self.mapping:
                lexemes = {dest: lexemes[source] for source, dest in self.mapping.items()}
            yield LexedRegion(start_match.start(), source_end, lexemes)
