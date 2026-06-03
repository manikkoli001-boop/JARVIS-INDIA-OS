import unittest
from unittest.mock import MagicMock

from core.agent import Agent
from core.memory.memory_manager import MemoryManager
from core.tool_manager import ToolManager


class AgentExtendedTest(unittest.TestCase):

    def setUp(self):
        self.tool_manager = ToolManager()
        self.memory = MemoryManager()
        self.mock_llm = MagicMock()
        self.agent = Agent(tool_manager=self.tool_manager, llm_client=self.mock_llm, memory=self.memory)

    def test_parse_direct_tool_response(self):
        self.mock_llm.query.return_value = '{"tool": "calculator", "parameters": {"expression": "1+1"}, "reply": "2"}'
        plan = self.agent.plan("Compute 1+1")
        self.assertEqual(plan.steps[0].tool, "calculator")
        self.assertEqual(plan.final_answer, "2")

    def test_recovery_prompts_callback(self):
        self.mock_llm.query.side_effect = [
            '{"goal": "Break a task", "steps": [{"name": "Fail", "description": "Fail intentionally", "tool": "unknown_tool", "parameters": {}}]}',
            "I will retry with a better plan."
        ]
        plan = self.agent.plan("Do something")
        self.agent.execute_plan(plan)
        self.assertIsNotNone(plan.steps[0].error)


if __name__ == "__main__":
    unittest.main()
