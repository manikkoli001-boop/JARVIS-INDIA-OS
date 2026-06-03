import unittest
from unittest.mock import MagicMock

from core.agent import Agent
from core.memory.memory_manager import MemoryManager
from core.tool_manager import ToolManager


class AgentTest(unittest.TestCase):

    def setUp(self):
        self.tool_manager = ToolManager()
        self.memory = MemoryManager()
        self.mock_llm = MagicMock()
        self.agent = Agent(tool_manager=self.tool_manager, llm_client=self.mock_llm, memory=self.memory)
        self.mock_llm.query.return_value = '{"goal": "Add numbers", "steps": [{"name": "Compute", "description": "Compute 2+2", "tool": "calculator", "parameters": {"expression": "2+2"}}], "final_answer": "4"}'

    def test_plan_parses_llm_response(self):
        plan = self.agent.plan("Calculate 2+2")
        self.assertEqual(plan.goal, "Add numbers")
        self.assertEqual(len(plan.steps), 1)
        self.assertEqual(plan.steps[0].tool, "calculator")

    def test_execute_plan_runs_tool(self):
        plan = self.agent.plan("Calculate 2+2")
        trace = self.agent.execute_plan(plan)
        self.assertEqual(trace[0].status, "completed")
        self.assertEqual(trace[0].result, "4")

    def test_run_task_returns_result(self):
        result = self.agent.run_task("Calculate 2+2")
        self.assertEqual(result["result"], "4")
        self.assertEqual(result["goal"], "Calculate 2+2")


if __name__ == "__main__":
    unittest.main()
