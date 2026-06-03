from __future__ import annotations

import logging
from typing import Optional

from core.agent import AgentPlan
from core.memory.memory_manager import MemoryManager
from core.tool_manager import ToolManager

from .checkpoint_engine import CheckpointEngine
from .enrichers import PlanEnricher
from .expanders import StepExpander
from .plan_contracts import PlanValidationResult
from .validators import PlannerValidator

logger = logging.getLogger(__name__)


class Planner:
    """Validate, enrich, normalize, and optionally checkpoint raw LLM plans."""

    def __init__(
        self,
        tool_manager: Optional[ToolManager] = None,
        memory_manager: Optional[MemoryManager] = None,
        validator: Optional[PlannerValidator] = None,
        enricher: Optional[PlanEnricher] = None,
        expander: Optional[StepExpander] = None,
        checkpoint_engine: Optional[CheckpointEngine] = None,
        insert_checkpoints: bool = False,
        logger: Optional[logging.Logger] = None,
    ):
        self.tool_manager = tool_manager or ToolManager()
        self.memory_manager = memory_manager
        self.validator = validator or PlannerValidator(tool_manager=self.tool_manager)
        self.enricher = enricher or PlanEnricher(
            tool_manager=self.tool_manager,
            memory_manager=self.memory_manager,
        )
        self.expander = expander or StepExpander(tool_manager=self.tool_manager)
        self.checkpoint_engine = checkpoint_engine or CheckpointEngine(tool_manager=self.tool_manager)
        self.insert_checkpoints = insert_checkpoints
        self.logger = logger or logging.getLogger(__name__)

    def optimize(self, plan: AgentPlan) -> AgentPlan:
        """Optimize the provided AgentPlan and preserve the raw plan on failure."""

        try:
            initial_validation = self.validate_plan(plan)
            if not initial_validation:
                self.logger.warning(
                    "Planner preserving raw plan because validation failed: %s",
                    initial_validation.errors,
                )
                return plan
            if initial_validation.warnings:
                self.logger.info("Planner validation warnings: %s", initial_validation.warnings)

            enriched_plan = self.enrich_plan(plan)
            normalized_plan = self.normalize_plan(enriched_plan)

            final_validation = self.validate_plan(normalized_plan)
            if not final_validation:
                self.logger.warning(
                    "Planner preserving raw plan because optimized plan failed validation: %s",
                    final_validation.errors,
                )
                return plan
            if final_validation.warnings:
                self.logger.info("Planner optimized plan warnings: %s", final_validation.warnings)

            if self.insert_checkpoints:
                return self.checkpoint_engine.insert_checkpoints(normalized_plan)
            return normalized_plan
        except Exception:
            self.logger.exception("Planner optimization failed; falling back to raw plan.")
            return plan

    def validate_plan(self, plan: AgentPlan) -> PlanValidationResult:
        """Validate the input plan shape and consistency."""

        return self.validator.validate_plan(plan)

    def enrich_plan(self, plan: AgentPlan) -> AgentPlan:
        """Enrich the plan with deterministic memory and tool context."""

        return self.enricher.enrich_plan(plan)

    def normalize_plan(self, plan: AgentPlan) -> AgentPlan:
        """Normalize and expand the plan so execution remains stable."""

        return self.expander.expand_plan(plan)

    def suggest_self_correction(self, plan: AgentPlan, error: Exception) -> AgentPlan:
        """Return the safest corrected version of a plan after an optimization error."""

        self.logger.warning("Planner self-correction requested after error: %s", error)
        return self.optimize(plan)
