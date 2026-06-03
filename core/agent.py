import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

from core.conversation_history import ConversationHistory
from core.llm_client import OllamaClient
from core.memory.memory_manager import MemoryManager, memory_manager
from core.tool_manager import ToolManager, ToolNotFoundError

logger = logging.getLogger(__name__)


@dataclass
class AgentStep:
    name: str
    description: str
    tool: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Optional[str] = None
    error: Optional[str] = None


@dataclass
class AgentPlan:
    goal: str
    steps: List[AgentStep] = field(default_factory=list)
    final_answer: Optional[str] = None


class PlanOptimizer(Protocol):
    def optimize(self, plan: AgentPlan) -> AgentPlan:
        ...


class Agent:
    """Intelligent reasoning and tool orchestration layer for Jarvis."""

    def __init__(
        self,
        tool_manager: Optional[ToolManager] = None,
        llm_client: Optional[OllamaClient] = None,
        memory: Optional[MemoryManager] = None,
        history: Optional[ConversationHistory] = None,
        planner: Optional[PlanOptimizer] = None,
    ):
        self.tool_manager = tool_manager or ToolManager()
        self.llm_client = llm_client or OllamaClient()
        self.memory = memory or memory_manager
        self.history = history or ConversationHistory()
        self.planner = planner if planner is not None else self._create_default_planner()

    def run_task(self, goal: str, max_steps: int = 5) -> Dict[str, Any]:
        raw_plan = self.plan(goal)
        plan = self._optimize_plan(raw_plan)
        trace = self.execute_plan(plan, max_steps=max_steps)
        return {
            "goal": goal,
            "plan": plan,
            "trace": [step.__dict__ for step in plan.steps],
            "result": plan.final_answer or (plan.steps[-1].result if plan.steps else ""),
        }

    def plan(self, goal: str) -> AgentPlan:
        prompt = self._build_planning_prompt(goal)
        response = self.llm_client.query(prompt)
        plan = self._parse_plan(response, goal)
        if not plan.steps:
            plan.steps.append(AgentStep(name="Answer directly", description="Answer without tools", tool=None, parameters={}))
            plan.final_answer = response
        return plan

    def execute_plan(self, plan: AgentPlan, max_steps: int = 5) -> List[AgentStep]:
        for index, step in enumerate(plan.steps[:max_steps], start=1):
            if step.tool:
                try:
                    step.status = "running"
                    result = self.tool_manager.execute_tool(step.tool, **step.parameters)
                    step.result = str(result)
                    step.status = "completed"
                    logger.info("Agent executed tool %s for step %s", step.tool, step.name)
                except ToolNotFoundError as exc:
                    step.error = str(exc)
                    step.status = "failed"
                    plan.final_answer = self._recover_from_failure(plan.goal, step, exc)
                    break
                except Exception as exc:
                    step.error = str(exc)
                    step.status = "failed"
                    plan.final_answer = self._recover_from_failure(plan.goal, step, exc)
                    break
            else:
                step.status = "skipped"
                step.result = step.description
            if index == len(plan.steps) and not plan.final_answer:
                plan.final_answer = step.result or "Task completed."
        return plan.steps

    def _recover_from_failure(self, goal: str, step: AgentStep, error: Exception) -> str:
        prompt = (
            f"The agent failed while executing step '{step.name}'.\n"
            f"Step description: {step.description}\n"
            f"Tool: {step.tool}\n"
            f"Parameters: {step.parameters}\n"
            f"Error: {error}\n"
            "Please suggest a corrected plan or recovery action in one sentence."
        )
        logger.warning("Agent recovery prompt: %s", prompt)
        return self.llm_client.query([
            {"role": "system", "content": "You are an agent recovery assistant."},
            {"role": "user", "content": prompt},
        ])

    def _build_planning_prompt(self, goal: str) -> List[Dict[str, str]]:
        tool_defs = self._format_tool_definitions()
        memory_text = self._build_memory_context(goal)
        conversation = self.history.as_prompt()
        system_prompt = (
            "You are Jarvis, an intelligent planner. Break the user's goal into sequential steps. "
            "Use tools when appropriate and return only valid JSON. "
            "The JSON should contain 'goal', 'steps', and optional 'final_answer'."
        )
        user_prompt = (
            f"Goal: {goal}\n\n"
            f"Available tools:\n{tool_defs}\n\n"
            f"Memory context:\n{memory_text}\n\n"
            f"Conversation history:\n{conversation}\n\n"
            "Return JSON like: {\"goal\": \"...\", \"steps\": [{\"name\": \"...\", \"description\": \"...\", \"tool\": \"tool_name\", \"parameters\": {...}}], \"final_answer\": \"...\"}."
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _format_tool_definitions(self) -> str:
        entries = []
        for tool_name in self.tool_manager.list_tools():
            metadata = self.tool_manager.get_tool_metadata(tool_name) or {}
            description = metadata.get("description", "No description available.")
            entries.append(f"- {tool_name}: {description}")
        return "\n".join(entries) if entries else "(no tools available)"

    def _build_memory_context(self, goal: str) -> str:
        recent = self.memory.list_recent_memories(limit=3)
        summary = []
        if recent:
            summary.append("Recent memories:")
            summary.extend(f"- {item['text']}" for item in recent)
        ranked = self.memory.search_memory(goal)
        if ranked:
            summary.append("Related memories:")
            summary.extend(f"- {item['text']}" for item in ranked[:3])
        return "\n".join(summary) if summary else "No memories available."

    def _parse_plan(self, response: str, goal: str) -> AgentPlan:
        if not response:
            return AgentPlan(goal=goal)
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                except json.JSONDecodeError:
                    data = {"goal": goal, "steps": []}
            else:
                data = {"goal": goal, "steps": []}

        steps = []
        if isinstance(data.get("steps"), list) and data["steps"]:
            for raw_step in data["steps"]:
                steps.append(AgentStep(
                    name=str(raw_step.get("name", "unnamed")),
                    description=str(raw_step.get("description", "")),
                    tool=raw_step.get("tool"),
                    parameters=raw_step.get("parameters", {}) if isinstance(raw_step.get("parameters", {}), dict) else {},
                ))
            final_answer = data.get("final_answer")
        elif data.get("tool") is not None or data.get("reply") is not None:
            steps.append(AgentStep(
                name=data.get("tool") or "answer",
                description=data.get("reply", ""),
                tool=data.get("tool"),
                parameters=data.get("parameters", {}) if isinstance(data.get("parameters", {}), dict) else {},
            ))
            final_answer = data.get("reply")
        else:
            final_answer = response

        return AgentPlan(goal=str(data.get("goal", goal)), steps=steps, final_answer=final_answer)

    def _create_default_planner(self) -> Optional[PlanOptimizer]:
        try:
            from core.planner.planner import Planner

            return Planner(tool_manager=self.tool_manager, memory_manager=self.memory)
        except Exception:
            logger.exception("Failed to initialize planner; agent will use raw plans.")
            return None

    def _optimize_plan(self, plan: AgentPlan) -> AgentPlan:
        if self.planner is None:
            return plan

        try:
            optimized_plan = self.planner.optimize(plan)
        except Exception:
            logger.exception("Planner optimization failed; falling back to raw plan.")
            return plan

        if not isinstance(optimized_plan, AgentPlan):
            logger.error("Planner returned %s instead of AgentPlan; falling back to raw plan.", type(optimized_plan).__name__)
            return plan
        return optimized_plan
