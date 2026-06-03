from __future__ import annotations

import inspect
import logging
from typing import Any, List, Optional

from core.agent import AgentPlan, AgentStep
from core.tool_manager import ToolManager

from .plan_contracts import PlanValidationResult

logger = logging.getLogger(__name__)


class PlannerValidator:
    """Validate plan and step structures before optimization."""

    def __init__(self, tool_manager: Optional[ToolManager] = None, validate_tools: bool = True):
        self.tool_manager = tool_manager
        self.validate_tools = validate_tools

    def validate_plan(self, plan: AgentPlan) -> PlanValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not isinstance(plan, AgentPlan):
            return PlanValidationResult.invalid(["Plan must be an AgentPlan instance."])

        if not plan.goal or not isinstance(plan.goal, str):
            errors.append("Plan goal must be a non-empty string.")

        if not isinstance(plan.steps, list):
            errors.append("Plan steps must be a list.")
        else:
            for index, step in enumerate(plan.steps, start=1):
                result = self.validate_step(step, index)
                errors.extend(result.errors)
                warnings.extend(result.warnings)

        if errors:
            logger.debug("Plan validation failed with errors: %s", errors)
        if warnings:
            logger.debug("Plan validation completed with warnings: %s", warnings)

        return PlanValidationResult(is_valid=not errors, errors=errors, warnings=warnings)

    def validate_step(self, step: Any, index: int = 0) -> PlanValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not isinstance(step, AgentStep):
            return PlanValidationResult.invalid([f"Step {index} must be an AgentStep instance."])

        if not step.name or not isinstance(step.name, str):
            errors.append(f"Step {index} name must be a non-empty string.")

        if not isinstance(step.description, str):
            errors.append(f"Step {index} description must be a string.")

        if not isinstance(step.parameters, dict):
            errors.append(f"Step {index} parameters must be a dictionary.")

        if step.tool is not None and not isinstance(step.tool, str):
            errors.append(f"Step {index} tool identifier must be a string if provided.")

        if self.validate_tools and self.tool_manager is not None and isinstance(step.tool, str):
            warnings.extend(self._validate_tool_reference(step, index))

        return PlanValidationResult(is_valid=not errors, errors=errors, warnings=warnings)

    def _validate_tool_reference(self, step: AgentStep, index: int) -> List[str]:
        warnings: List[str] = []
        tool_name = (step.tool or "").strip()
        tool = self.tool_manager.get_tool(tool_name)
        if tool is None:
            warnings.append(f"Step {index} references unknown tool '{tool_name}'.")
            return warnings

        func = tool.get("function")
        if not callable(func):
            warnings.append(f"Step {index} references tool '{tool_name}' without a callable function.")
            return warnings

        signature = inspect.signature(func)
        accepts_var_kwargs = any(
            parameter.kind is inspect.Parameter.VAR_KEYWORD
            for parameter in signature.parameters.values()
        )
        if accepts_var_kwargs:
            return warnings

        provided = set(step.parameters)
        expected = {
            name
            for name, parameter in signature.parameters.items()
            if parameter.kind in {inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY}
        }
        unknown = sorted(provided - expected)
        if unknown:
            warnings.append(
                f"Step {index} provides unsupported parameter(s) for tool '{tool_name}': {', '.join(unknown)}."
            )

        missing = [
            name
            for name, parameter in signature.parameters.items()
            if parameter.default is inspect.Signature.empty
            and parameter.kind in {inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY}
            and name not in provided
        ]
        if missing:
            warnings.append(
                f"Step {index} is missing required parameter(s) for tool '{tool_name}': {', '.join(missing)}."
            )

        return warnings
