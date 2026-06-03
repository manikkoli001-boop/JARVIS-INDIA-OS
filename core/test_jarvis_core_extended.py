import unittest
from unittest.mock import MagicMock, patch

from core.jarvis_core import JarvisAICore
from core.intent_classifier import IntentResult
from core.tool_manager import ToolNotFoundError


class JarvisCoreExtendedTest(unittest.TestCase):

    def setUp(self):
        self.mock_tool_manager = MagicMock()
        self.mock_llm = MagicMock()
        self.mock_memory = MagicMock()
        self.mock_history = MagicMock()
        self.mock_classifier = MagicMock()
        self.core = JarvisAICore(
            tool_manager=self.mock_tool_manager,
            llm_client=self.mock_llm,
            memory=self.mock_memory,
            history=self.mock_history,
            classifier=self.mock_classifier,
        )

    def test_format_tool_definitions_when_tools_exist(self):
        self.mock_tool_manager.list_tools.return_value = ["calculator"]
        self.mock_tool_manager.get_tool_metadata.return_value = {"description": "Add numbers."}
        formatted = self.core._format_tool_definitions()
        self.assertIn("calculator", formatted)
        self.assertIn("Add numbers.", formatted)

    def test_build_memory_context_with_recent_and_related(self):
        self.mock_memory.list_recent_memories.return_value = [
            {"text": "Remember this", "category": "note"}
        ]
        self.mock_memory.search_memory.return_value = [
            {"text": "Related item", "category": "note"}
        ]
        context = self.core._build_memory_context("Remember")
        self.assertIn("- Remember this (note)", context)
        self.assertIn("Related memories", context)

    def test_parse_llm_response_with_embedded_json(self):
        raw = "Some text {\"tool\": \"calculator\", \"parameters\": {\"expression\": \"1+2\"}, \"reply\": \"3\"}"
        parsed = self.core._parse_llm_response(raw)
        self.assertEqual(parsed["tool"], "calculator")
        self.assertEqual(parsed["parameters"], {"expression": "1+2"})
        self.assertEqual(parsed["reply"], "3")

    def test_fallback_intent_uses_tool_when_confident(self):
        self.mock_classifier.classify.return_value = IntentResult(
            tool_name="calculator",
            intent="tool",
            confidence=0.9,
            command="Calculate 2+2",
            parameters={"expression": "2+2"},
        )
        result = self.core._fallback_intent("Calculate 2+2", {"tool": None, "parameters": {}, "reply": ""})
        self.assertEqual(result["tool"], "calculator")

    def test_execute_tool_handles_tool_not_found(self):
        self.mock_tool_manager.execute_tool.side_effect = ToolNotFoundError("missing")
        result = self.core._execute_tool("bad_tool", {})
        self.assertIn("could not execute tool", result)

    def test_should_save_memory_rejects_question(self):
        self.assertFalse(self.core._should_save_memory("What is the weather?"))

    def test_should_save_memory_accepts_statement(self):
        self.assertTrue(self.core._should_save_memory("I want to remember this conversation about code."))

    def test_auto_save_memory_exception_is_handled(self):
        self.mock_memory.save_memory.side_effect = ValueError("fail")
        self.core._auto_save_memory("A safe message")
        self.mock_memory.save_memory.assert_called_once()


if __name__ == "__main__":
    unittest.main()
