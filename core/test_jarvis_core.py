import unittest
from unittest.mock import MagicMock

from core.jarvis_core import JarvisAICore
from core.llm_client import OllamaClient
from core.memory.memory_manager import MemoryManager
from core.tool_manager import ToolManager


class JarvisAICoreTest(unittest.TestCase):

    def setUp(self):
        self.mock_llm = MagicMock(spec=OllamaClient)
        self.mock_memory = MagicMock(spec=MemoryManager)
        self.mock_memory.list_recent_memories.return_value = []
        self.mock_memory.search_memory.return_value = []
        self.mock_memory.save_memory.return_value = {"id": 1}
        self.core = JarvisAICore(tool_manager=ToolManager(), llm_client=self.mock_llm, memory=self.mock_memory)

    def test_process_invokes_tool_when_llm_selects_tool(self):
        self.mock_llm.query.return_value = '{"tool": "calculator", "parameters": {"expression": "2+2"}, "reply": ""}'
        result = self.core.process("Please calculate 2+2")
        self.assertEqual(result["tool"], "calculator")
        self.assertEqual(result["result"], "4")

    def test_process_returns_llm_reply_when_no_tool(self):
        self.mock_llm.query.return_value = '{"tool": null, "parameters": {}, "reply": "Hello, I can help with that."}'
        result = self.core.process("Hello Jarvis")
        self.assertIsNone(result["tool"])
        self.assertEqual(result["result"], "Hello, I can help with that.")

    def test_fallback_to_classifier_if_llm_does_not_select_tool(self):
        self.mock_llm.query.return_value = '{"tool": null, "parameters": {}, "reply": ""}'
        result = self.core.process("Calculate 3+3")
        self.assertEqual(result["tool"], "calculator")
        self.assertEqual(result["result"], "6")

    def test_auto_save_memory_for_statement(self):
        self.mock_llm.query.return_value = '{"tool": null, "parameters": {}, "reply": "I heard you."}'
        self.core.process("Remember that I like building AI projects.")
        self.mock_memory.save_memory.assert_called_once()


if __name__ == "__main__":
    unittest.main()
