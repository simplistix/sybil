import threading
from dataclasses import dataclass, field
from typing import Any
from unittest import SkipTest

from sybil import Document, Example
from sybil.example import NotEvaluated
from sybil.region import Region


class If:
    def __init__(self, default_reason: str) -> None:
        self.default_reason = default_reason

    def __call__(self, condition: Any, reason: str | None = None) -> str | None:
        if condition:
            return reason or self.default_reason
        return None


@dataclass
class _DirectiveInfo:
    region: Region
    action: str
    raw_reason: str | None
    structural_error: Exception | None = None
    covered: list[Region] = field(default_factory=list)
    resolved: bool = False
    disabled: bool = False
    exception: Exception | None = None
    resolution_error: Exception | None = None


@dataclass
class _DocPlan:
    info_for_directive: dict[int, _DirectiveInfo] = field(default_factory=dict)
    directive_for_covered: dict[int, _DirectiveInfo] = field(default_factory=dict)


class Skipper:
    def __init__(self, directive: str) -> None:
        self.directive = directive
        self._plans: dict[int, _DocPlan] = {}
        self._lock = threading.Lock()

    def _build_plan(self, document: Document) -> _DocPlan:
        plan = _DocPlan()
        directive_label = self.directive
        pending_next: _DirectiveInfo | None = None
        current_start: _DirectiveInfo | None = None
        last_action: str | None = None

        for _, region in document.regions:
            if region.evaluator is self:
                action, reason = region.parsed
                info = _DirectiveInfo(region=region, action=action, raw_reason=reason)
                plan.info_for_directive[id(region)] = info

                if action not in ('start', 'next', 'end'):
                    info.structural_error = ValueError('Bad skip action: ' + action)
                    continue

                if last_action is None and action not in ('start', 'next'):
                    info.structural_error = ValueError(
                        f"'{directive_label}: {action}' must follow '{directive_label}: start'"
                    )
                    continue
                if last_action and action != 'end':
                    info.structural_error = ValueError(
                        f"'{directive_label}: {action}' cannot follow "
                        f"'{directive_label}: {last_action}'"
                    )
                    continue

                if action == 'end' and reason:
                    info.structural_error = ValueError("Cannot have condition on 'skip: end'")
                    last_action = None
                    current_start = None
                    continue

                if action == 'next':
                    pending_next = info
                    last_action = 'next'
                elif action == 'start':
                    current_start = info
                    last_action = 'start'
                elif action == 'end':
                    current_start = None
                    last_action = None
            else:
                if pending_next is not None:
                    pending_next.covered.append(region)
                    plan.directive_for_covered[id(region)] = pending_next
                    pending_next = None
                    last_action = None
                elif current_start is not None:
                    current_start.covered.append(region)
                    plan.directive_for_covered[id(region)] = current_start

        return plan

    def _plan_for(self, document: Document) -> _DocPlan:
        key = id(document)
        with self._lock:
            plan = self._plans.get(key)
            if plan is None:
                plan = self._build_plan(document)
                self._plans[key] = plan
        return plan

    def _resolve(self, info: _DirectiveInfo, document: Document) -> None:
        with self._lock:
            if info.resolved:
                return
            reason = info.raw_reason
            try:
                if reason:
                    namespace = document.namespace.copy()
                    reason = reason.lstrip()
                    if reason.startswith('if'):
                        condition = reason[2:]
                        reason = 'if_' + condition
                        namespace['if_'] = If(condition)
                    resolved_reason = eval(reason, namespace)
                    if resolved_reason:
                        info.exception = SkipTest(resolved_reason)
                    else:
                        info.disabled = True
                # else: plain directive with no condition — covered examples
                # fall through to a silent skip in __call__.
            except Exception as exc:
                info.resolution_error = exc
            finally:
                info.resolved = True

    def __call__(self, example: Example) -> None:
        document = example.document
        plan = self._plan_for(document)
        region_id = id(example.region)

        directive_info = plan.info_for_directive.get(region_id)
        if directive_info is not None:
            if directive_info.structural_error is not None:
                raise directive_info.structural_error
            self._resolve(directive_info, document)
            if directive_info.resolution_error is not None:
                raise directive_info.resolution_error
            return

        covering = plan.directive_for_covered.get(region_id)
        if covering is None:
            raise NotEvaluated()

        self._resolve(covering, document)
        if covering.resolution_error is not None or covering.disabled:
            raise NotEvaluated()
        if covering.exception is not None:
            raise covering.exception
        # Plain skip directive (no condition) — silently swallow this example.
        return
