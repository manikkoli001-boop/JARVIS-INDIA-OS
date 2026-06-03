from __future__ import annotations

import logging
from typing import List, Optional

from core.agent import AgentPlan, AgentStep
from core.memory.memory_manager import MemoryManager
from core.tool_manager import ToolManager

from .plan_contracts import clone_plan, clone_step

logger = logging.getLogger(__name__)


class PlanEnricher:
    """Apply deterministic context and tool metadata enrichment to plans."""

    def __init__(
        self,
        tool_manager: Optional[ToolManager] = None,
        memory_manager: Optional[MemoryManager] = None,
        memory_limit: int = 3,
    ):
        self.tool_manager = tool_manager
        self.memory_manager = memory_manager
        self.memory_limit = max(0, memory_limit)

    def enrich_plan(self, plan: AgentPlan) -> AgentPlan:
        """Return an enriched copy of the plan without mutating the raw plan."""

        goal = plan.goal.strip()
        memory_hints = self._memory_hints(goal)
        enriched_steps = [self.enrich_step(step, memory_hints) for step in plan.steps]
        return clone_plan(plan, goal=goal, steps=enriched_steps)

    def enrich_step(self, step: AgentStep, memory_hints: List[str]) -> AgentStep:
        """Enrich a single step with safe deterministic defaults."""

        name = step.name.strip() or self._default_step_name(step)
        tool = step.tool.strip() if isinstance(step.tool, str) and step.tool.strip() else None
        description = step.description.strip()

        if not description and tool:
            description = self._tool_description(tool)
        if not description:
            description = self._direct_description(memory_hints)

        return clone_step(step, name=name, description=description, tool=tool)

    def _default_step_name(self, step: AgentStep) -> str:
        if step.tool:
            return f"Use {step.tool}"
        return "Answer directly"

    def _tool_description(self, tool_name: str) -> str:
        if self.tool_manager is None:
            return f"Execute tool '{tool_name}'."

        metadata = self.tool_manager.get_tool_metadata(tool_name)
        if not metadata:
            logger.warning("Planner could not enrich unknown tool '%s'.", tool_name)
            return f"Execute tool '{tool_name}'."

        description = str(metadata.get("description", "")).strip()
        return description or f"Execute tool '{tool_name}'."

    def _direct_description(self, memory_hints: List[str]) -> str:
        if not memory_hints:
            return "Answer directly using the conversation context."
        return "Answer directly using the conversation context and relevant memory."

    def _memory_hints(self, goal: str) -> List[str]:
        if self.memory_manager is None or self.memory_limit <= 0:
            return []

        try:
            results = self.memory_manager.search_memory(goal)
        except Exception:
            logger.exception("Planner memory enrichment failed for goal '%s'.", goal)
            return []

        hints: List[str] = []
        for item in results[: self.memory_limit]:
            text = str(item.get("text", "")).strip()
            if text:
                hints.append(text)
        return hints
