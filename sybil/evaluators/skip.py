from dataclasses import dataclass
from typing import Optional, Dict
from unittest import SkipTest

from sybil import Example, Document
from sybil.typing import Evaluator


class If:

    def __init__(self, default_reason) -> None:
        self.default_reason = default_reason

    def __call__(self, condition, reason=None):
        if condition:
            return reason or self.default_reason


@dataclass
class SkipState:
    original_evaluator: Optional[Evaluator]
    remove: bool = False
    exception: Optional[Exception] = None
    last_action: str = None


class Skipper:

    def __init__(self) -> None:
        self.document_state: Dict[Document, SkipState] = {}

    def state_for(self, example: Example) -> SkipState:
        document = example.document
        if document not in self.document_state:
            self.document_state[document] = SkipState(document.evaluator)
        return self.document_state[example.document]

    def maybe_install(self, example: Example, state: SkipState, condition: Optional[str]) -> None:
        document = example.document
        install = True
        if condition:
            namespace = document.namespace.copy()
            namespace['if_'] = If(condition)
            reason = eval('if_'+condition, namespace)
            if reason:
                state.exception = SkipTest(reason)
            else:
                install = False
        if install and document.evaluator is not self:
            document.evaluator = self

    def remove(self, example: Example) -> None:
        document = example.document
        state = self.state_for(example)
        document.evaluator = state.original_evaluator
        del self.document_state[document]

    def evaluate_skip_example(self, example: Example):
        state = self.state_for(example)
        action, condition = example.parsed

        if action not in ('start', 'next', 'end'):
            raise ValueError('Bad skip action: ' + action)
        if state.last_action is None and action not in ('start', 'next'):
            raise ValueError(f"'skip: {action}' must follow 'skip: start'")
        elif state.last_action and action !='end':
            raise ValueError(f"'skip: {action}' cannot follow 'skip: {state.last_action}'")

        state.last_action = action

        if action == 'start':
            self.maybe_install(example, state, condition)
        elif action == 'next':
            self.maybe_install(example, state, condition)
            state.remove = True
        elif action == 'end':
            self.remove(example)
            if condition:
                raise ValueError("Cannot have condition on 'skip: end'")

    def evaluate_other_example(self, example: Example) -> None:
        state = self.state_for(example)
        if state.remove:
            self.remove(example)
            state.remove = False
        if state.exception is not None:
            raise state.exception

    def __call__(self, example: Example) -> None:
        if example.region.evaluator is self:
            self.evaluate_skip_example(example)
        else:
            self.evaluate_other_example(example)
