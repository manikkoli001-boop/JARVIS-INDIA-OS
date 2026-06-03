from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List, Optional, Set

from core.agent import AgentPlan, AgentStep
from core.tool_manager import ToolManager

from .plan_contracts import clone_plan

logger = logging.getLogger(__name__)


@dataclass
class CheckpointStep(AgentStep):
    """Non-executing checkpoint inserted before sensitive or privileged work."""

    checkpoint_type: str = "confirmation"
    prompt: str = ""


class CheckpointEngine:
    """Insert and manage checkpoints in an AgentPlan for safe execution."""

    def __init__(
        self,
        tool_manager: Optional[ToolManager] = None,
        privileged_permissions: Optional[Iterable[str]] = None,
    ):
        self.tool_manager = tool_manager
        self.privileged_permissions: Set[str] = {
            permission.strip().lower()
            for permission in (privileged_permissions or {"admin", "power", "system"})
            if permission.strip()
        }

    def insert_checkpoints(self, plan: AgentPlan) -> AgentPlan:
        """Add checkpoint steps before operations that require explicit review."""

        if not plan.steps:
            return plan

        enriched_steps: List[AgentStep] = []
        for step in plan.steps:
            if self.requires_checkpoint(step):
                checkpoint = self.create_checkpoint_step(step)
                logger.info("Planner inserted checkpoint before step '%s'.", step.name)
                enriched_steps.append(checkpoint)
            enriched_steps.append(step)

        return clone_plan(plan, steps=enriched_steps)

    def requires_checkpoint(self, step: AgentStep) -> bool:
        """Determine whether a step should be gated by a checkpoint."""

        if not step.tool or self.tool_manager is None:
            return False

        metadata = self.tool_manager.get_tool_metadata(step.tool)
        if not metadata:
            return False

        permission = str(metadata.get("permission", "user")).strip().lower()
        sensitive = bool(metadata.get("sensitive", False))
        if sensitive or permission in self.privileged_permissions:
            return True

        tool_name = step.tool.strip().lower()
        return tool_name.startswith(("open_", "close_", "system_")) or tool_name.endswith("_delete")

    def create_checkpoint_step(self, step: AgentStep) -> CheckpointStep:
        """Create a checkpoint step for a given executable step."""

        prompt = (
            f"Confirm execution of step '{step.name}'"
            + (f" using tool '{step.tool}'" if step.tool else "")
            + "."
        )
        return CheckpointStep(
            name=f"Confirm {step.name}",
            description="Review and approve the following sensitive or side-effecting step before execution.",
            tool=None,
            parameters={},
            checkpoint_type="confirmation",
            prompt=prompt,
        )
