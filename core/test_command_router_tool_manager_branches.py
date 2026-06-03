import unittest
from unittest.mock import MagicMock

from core.command_router import CommandRouter
from core.intent_classifier import IntentResult
from core.tool_manager import ToolNotFoundError


class CommandRouterToolManagerBranchesTest(unittest.TestCase):

    def setUp(self):
        self.mock_tool_manager = MagicMock()
        self.mock_classifier = MagicMock()
        self.router = CommandRouter(tool_manager=self.mock_tool_manager, classifier=self.mock_classifier)

    def test_route_unknown_intent(self):
        self.mock_classifier.classify.return_value = IntentResult(tool_name=None, intent="unknown", confidence=0.0, command="Tell me a joke", parameters={})
        result = self.router.route("Tell me a joke")
        self.assertEqual(result["tool"], None)
        self.assertEqual(result["intent"], "unknown")

    def test_route_tool_not_found(self):
        self.mock_classifier.classify.return_value = IntentResult(tool_name="missing", intent="tool", confidence=0.8, command="Missing tool", parameters={})
        self.mock_tool_manager.execute_tool.side_effect = ToolNotFoundError("missing")
        result = self.router.route("Missing tool")
        self.assertEqual(result["tool"], "missing")
        self.assertIn("not available", result["result"])

    def test_route_type_error(self):
        self.mock_classifier.classify.return_value = IntentResult(tool_name="calculator", intent="tool", confidence=0.9, command="Calculate something", parameters={})
        self.mock_tool_manager.execute_tool.side_effect = TypeError("bad args")
        result = self.router.route("Calculate something")
        self.assertIn("argument error", result["result"])

    def test_route_generic_exception(self):
        self.mock_classifier.classify.return_value = IntentResult(tool_name="danger", intent="tool", confidence=0.5, command="Dangerous operation", parameters={})
        self.mock_tool_manager.execute_tool.side_effect = ValueError("boom")
        result = self.router.route("Dangerous operation")
        self.assertIn("An error occurred", result["result"])


if __name__ == "__main__":
    unittest.main()
