from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Iterable, List, Mapping, Optional, Sequence

from core.agent import AgentPlan, AgentStep

_UNSET = object()


@dataclass(frozen=True)
class PlanValidationResult:
    """Validation outcome for an agent plan."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid

    @classmethod
    def ok(cls, warnings: Optional[Iterable[str]] = None) -> "PlanValidationResult":
        return cls(is_valid=True, warnings=list(warnings or []))

    @classmethod
    def invalid(
        cls,
        errors: Iterable[str],
        warnings: Optional[Iterable[str]] = None,
    ) -> "PlanValidationResult":
        return cls(is_valid=False, errors=list(errors), warnings=list(warnings or []))

    def merge(self, other: "PlanValidationResult") -> "PlanValidationResult":
        errors = [*self.errors, *other.errors]
        warnings = [*self.warnings, *other.warnings]
        return PlanValidationResult(is_valid=not errors, errors=errors, warnings=warnings)


@dataclass(frozen=True)
class ToolResolution:
    """Resolved tool metadata used by planner components."""

    name: str
    exists: bool
    description: str = ""
    sensitive: bool = False
    permission: str = "user"
    accepts_var_kwargs: bool = False


def clone_step(
    step: AgentStep,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tool: Any = _UNSET,
    parameters: Optional[Mapping[str, Any]] = None,
    status: Optional[str] = None,
    result: Any = _UNSET,
    error: Any = _UNSET,
) -> AgentStep:
    """Create an AgentStep copy while preserving unknown future behavior."""

    return AgentStep(
        name=step.name if name is None else name,
        description=step.description if description is None else description,
        tool=step.tool if tool is _UNSET else tool,
        parameters=dict(step.parameters if parameters is None else parameters),
        status=step.status if status is None else status,
        result=step.result if result is _UNSET else result,
        error=step.error if error is _UNSET else error,
    )


def clone_plan(
    plan: AgentPlan,
    *,
    goal: Optional[str] = None,
    steps: Optional[Sequence[AgentStep]] = None,
    final_answer: Any = _UNSET,
) -> AgentPlan:
    """Create an AgentPlan copy without mutating the original plan."""

    return AgentPlan(
        goal=plan.goal if goal is None else goal,
        steps=list(plan.steps if steps is None else steps),
        final_answer=plan.final_answer if final_answer is _UNSET else final_answer,
    )


def stable_parameters(parameters: Mapping[str, Any]) -> str:
    """Return a deterministic string representation for deduplication."""

    try:
        return json.dumps(parameters, sort_keys=True, default=str)
    except TypeError:
        return repr(sorted(parameters.items(), key=lambda item: str(item[0])))


def step_identity(step: AgentStep) -> str:
    """Build a stable identity for equivalent plan steps."""

    return "|".join(
        [
            step.name.strip().lower(),
            step.description.strip().lower(),
            str(step.tool or "").strip().lower(),
            stable_parameters(step.parameters),
        ]
    )


def validate_agent_plan(plan: AgentPlan) -> PlanValidationResult:
    """Validate the structural shape of an AgentPlan."""

    errors: List[str] = []

    if not isinstance(plan, AgentPlan):
        return PlanValidationResult.invalid(["Plan must be an AgentPlan instance."])

    if not plan.goal or not isinstance(plan.goal, str):
        errors.append("Plan goal must be a non-empty string.")

    if not isinstance(plan.steps, list):
        errors.append("Plan steps must be a list.")
    else:
        for index, step in enumerate(plan.steps, start=1):
            if not isinstance(step, AgentStep):
                errors.append(f"Step {index} must be an AgentStep instance.")
                continue
            if not step.name or not isinstance(step.name, str):
                errors.append(f"Step {index} name must be a non-empty string.")
            if not isinstance(step.description, str):
                errors.append(f"Step {index} description must be a string.")
            if not isinstance(step.parameters, dict):
                errors.append(f"Step {index} parameters must be a dictionary.")
            if step.tool is not None and not isinstance(step.tool, str):
                errors.append(f"Step {index} tool identifier must be a string if provided.")

    return PlanValidationResult(is_valid=not errors, errors=errors)
