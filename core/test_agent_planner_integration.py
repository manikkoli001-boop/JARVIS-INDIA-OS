import unittest
from unittest.mock import MagicMock

from core.agent import Agent, AgentPlan
from core.memory.memory_manager import MemoryManager
from core.tool_manager import ToolManager


class PlannerSpy:
    def __init__(self):
        self.called = False

    def optimize(self, plan: AgentPlan) -> AgentPlan:
        self.called = True
        return plan


class BrokenPlanner:
    def optimize(self, plan: AgentPlan) -> AgentPlan:
        raise RuntimeError("planner unavailable")


class AgentPlannerIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.tool_manager = ToolManager()
        self.memory = MemoryManager()
        self.mock_llm = MagicMock()
        self.mock_llm.query.return_value = (
            '{"goal": "Add numbers", "steps": [{"name": "Compute", '
            '"description": "Compute 2+2", "tool": "calculator", '
            '"parameters": {"expression": "2+2"}}], "final_answer": "4"}'
        )

    def test_run_task_calls_injected_planner(self):
        planner = PlannerSpy()
        agent = Agent(
            tool_manager=self.tool_manager,
            llm_client=self.mock_llm,
            memory=self.memory,
            planner=planner,
        )

        result = agent.run_task("Calculate 2+2")

        self.assertTrue(planner.called)
        self.assertEqual(result["result"], "4")

    def test_run_task_falls_back_to_raw_plan_when_planner_fails(self):
        agent = Agent(
            tool_manager=self.tool_manager,
            llm_client=self.mock_llm,
            memory=self.memory,
            planner=BrokenPlanner(),
        )

        result = agent.run_task("Calculate 2+2")

        self.assertEqual(result["result"], "4")
        self.assertEqual(result["plan"].goal, "Add numbers")


if __name__ == "__main__":
    unittest.main()
