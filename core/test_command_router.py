import unittest

from core.command_router import CommandRouter
from core.intent_classifier import IntentClassifier
from core.tool_manager import ToolManager


class IntentClassifierTest(unittest.TestCase):

    def setUp(self):
        self.classifier = IntentClassifier()

    def test_classify_calculator_intent(self):
        result = self.classifier.classify("Calculate 3 + 7")
        self.assertEqual(result.tool_name, "calculator")
        self.assertGreaterEqual(result.confidence, 0.3)

    def test_classify_system_info_intent(self):
        result = self.classifier.classify("Show me system info")
        self.assertEqual(result.tool_name, "system_info")
        self.assertGreater(result.confidence, 0.0)

    def test_classify_memory_save_intent(self):
        result = self.classifier.classify("Remember this as a task")
        self.assertEqual(result.tool_name, "memory_save")
        self.assertIn("category", result.parameters)
        self.assertEqual(result.parameters["category"], "task")

    def test_classify_memory_delete_intent(self):
        result = self.classifier.classify("Delete memory 42")
        self.assertEqual(result.tool_name, "memory_delete")
        self.assertEqual(result.parameters["memory_id"], 42)


class CommandRouterTest(unittest.TestCase):

    def setUp(self):
        self.router = CommandRouter(tool_manager=ToolManager(), classifier=IntentClassifier())

    def test_route_calculator(self):
        response = self.router.route("Calculate 2+2")
        self.assertEqual(response["tool"], "calculator")
        self.assertEqual(response["result"], "4")

    def test_route_system_info(self):
        response = self.router.route("Show me the system details")
        self.assertEqual(response["tool"], "system_info")
        self.assertIn("platform:", response["result"])

    def test_route_memory_save(self):
        response = self.router.route("Remember learn Python as a project")
        self.assertEqual(response["tool"], "memory_save")
        self.assertIn("Memory saved", response["result"])

    def test_route_unknown_command(self):
        response = self.router.route("Tell me a joke")
        self.assertEqual(response["tool"], None)
        self.assertEqual(response["intent"], "unknown")

    def test_route_memory_delete_without_id(self):
        response = self.router.route("Delete memory please")
        self.assertEqual(response["tool"], "memory_delete")
        self.assertIn("argument error", response["result"].lower())


if __name__ == "__main__":
    unittest.main()
