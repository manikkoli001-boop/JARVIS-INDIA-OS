from __future__ import annotations

import inspect
import logging
import types
from typing import Any, Dict, List, Mapping, Optional, Union, get_args, get_origin

from core.agent import AgentPlan, AgentStep
from core.tool_manager import ToolManager

from .plan_contracts import clone_plan, clone_step, step_identity

logger = logging.getLogger(__name__)

_COMPOUND_STEP_KEYS = ("__compound_steps__", "__steps__", "substeps")


class StepExpander:
    """Convert high-level plan steps into executable, normalized steps."""

    def __init__(self, tool_manager: Optional[ToolManager] = None):
        self.tool_manager = tool_manager

    def expand_plan(self, plan: AgentPlan) -> AgentPlan:
        """Expand structured compound steps and remove exact duplicate work."""

        expanded_steps: List[AgentStep] = []
        seen: set[str] = set()
        for step in plan.steps:
            for expanded_step in self.expand_step(step):
                normalized = self._normalize_step(expanded_step)
                identity = step_identity(normalized)
                if identity in seen:
                    logger.info("Planner removed duplicate step '%s'.", normalized.name)
                    continue
                seen.add(identity)
                expanded_steps.append(normalized)

        return clone_plan(plan, steps=expanded_steps)

    def expand_step(self, step: AgentStep) -> List[AgentStep]:
        """Expand a single step into one or more executable steps."""

        compound_steps = self._extract_compound_steps(step)
        if not compound_steps:
            return [self._normalize_step(step)]

        logger.info("Planner expanding compound step '%s' into %d step(s).", step.name, len(compound_steps))
        return [self._step_from_mapping(item, step, index) for index, item in enumerate(compound_steps, start=1)]

    def _extract_compound_steps(self, step: AgentStep) -> List[Mapping[str, Any]]:
        if step.tool:
            return []

        for key in _COMPOUND_STEP_KEYS:
            raw_steps = step.parameters.get(key)
            if isinstance(raw_steps, list) and all(isinstance(item, Mapping) for item in raw_steps):
                return list(raw_steps)
        return []

    def _step_from_mapping(self, item: Mapping[str, Any], parent: AgentStep, index: int) -> AgentStep:
        raw_parameters = item.get("parameters", {})
        parameters = dict(raw_parameters) if isinstance(raw_parameters, Mapping) else {}
        name = str(item.get("name") or f"{parent.name} step {index}").strip()
        description = str(item.get("description") or parent.description).strip()
        raw_tool = item.get("tool")
        tool = str(raw_tool).strip() if raw_tool is not None and str(raw_tool).strip() else None
        return AgentStep(name=name, description=description, tool=tool, parameters=parameters)

    def _normalize_step(self, step: AgentStep) -> AgentStep:
        name = step.name.strip() or "Unnamed step"
        description = step.description.strip()
        tool = step.tool.strip() if isinstance(step.tool, str) and step.tool.strip() else None
        parameters = self._normalize_parameters(tool, step.parameters)
        return clone_step(step, name=name, description=description, tool=tool, parameters=parameters)

    def _normalize_parameters(self, tool_name: Optional[str], parameters: Mapping[str, Any]) -> Dict[str, Any]:
        safe_parameters = {
            str(key).strip(): value
            for key, value in dict(parameters).items()
            if str(key).strip() and str(key).strip() not in _COMPOUND_STEP_KEYS
        }
        if not tool_name or self.tool_manager is None:
            return safe_parameters

        metadata = self.tool_manager.get_tool(tool_name)
        if metadata is None:
            return safe_parameters

        func = metadata.get("function")
        if not callable(func):
            return safe_parameters

        signature = inspect.signature(func)
        accepts_var_kwargs = any(
            parameter.kind is inspect.Parameter.VAR_KEYWORD
            for parameter in signature.parameters.values()
        )
        if accepts_var_kwargs:
            return safe_parameters

        normalized: Dict[str, Any] = {}
        for name, parameter in signature.parameters.items():
            if parameter.kind not in {inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY}:
                continue
            if name not in safe_parameters:
                continue
            normalized[name] = self._cast_value(safe_parameters[name], parameter.annotation)

        dropped = sorted(set(safe_parameters) - set(normalized))
        if dropped:
            logger.info("Planner dropped unsupported parameter(s) for tool '%s': %s", tool_name, ", ".join(dropped))
        return normalized

    def _cast_value(self, value: Any, annotation: Any) -> Any:
        target = self._resolve_cast_target(annotation)
        if target is None or value is None or isinstance(value, target):
            return value

        try:
            if target is bool:
                return self._cast_bool(value)
            if target is int and not isinstance(value, bool):
                return int(value)
            if target is float and not isinstance(value, bool):
                return float(value)
            if target is str:
                return str(value)
        except (TypeError, ValueError):
            logger.debug("Planner could not cast value %r to %s.", value, target)
            return value
        return value

    def _resolve_cast_target(self, annotation: Any) -> Optional[type[Any]]:
        if annotation is inspect.Signature.empty:
            return None

        if isinstance(annotation, type):
            return annotation if annotation in {str, int, float, bool} else None

        origin = get_origin(annotation)
        if origin in {Union, types.UnionType}:
            candidates = [item for item in get_args(annotation) if item is not type(None)]
            for candidate in candidates:
                if isinstance(candidate, type) and candidate in {str, int, float, bool}:
                    return candidate
        return None

    def _cast_bool(self, value: Any) -> bool:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "y", "on"}:
                return True
            if normalized in {"0", "false", "no", "n", "off"}:
                return False
        return bool(value)
