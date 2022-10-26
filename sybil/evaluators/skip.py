from unittest import SkipTest

from sybil import Example


class If:

    def __init__(self, default_reason):
        self.default_reason = default_reason

    def __call__(self, condition, reason=None):
        if condition:
            return reason or self.default_reason


class Skip:

    def __init__(self, original_evaluator):
        self.original_evaluator = original_evaluator
        self.restore_next = False
        self.reason = None

    def __call__(self, example):
        document = example.document

        if self.restore_next:
            document.evaluator = self.original_evaluator

        if example.region.evaluator is evaluate_skip:

            action, condition = example.parsed

            if condition:

                if action == 'end':
                    raise ValueError('Cannot have condition on end')

                namespace = document.namespace.copy()
                namespace['If'] = If(condition)
                reason = eval('If'+condition, namespace)
                if reason:
                    self.reason = SkipTest(reason)
                else:
                    document.evaluator = self.original_evaluator
                    return

            if action == 'next':
                self.restore_next = True
            elif action == 'start':
                pass
            elif action == 'end':
                document.evaluator = self.original_evaluator
            else:
                raise ValueError('Bad skip action: '+action)

        elif self.reason:
            raise self.reason


def evaluate_skip(example: Example) -> None:
    evaluator = example.document.evaluator
    if not isinstance(evaluator, Skip):
        example.document.evaluator = evaluator = Skip(evaluator)
    evaluator(example)
