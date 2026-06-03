import unittest

from core.tool_manager import ToolManager, ToolNotFoundError


class ToolManagerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manager = ToolManager()

    def test_list_tools_contains_example_tools(self):
        names = self.manager.list_tools()
        self.assertIn("calculator", names)
        self.assertIn("system_info", names)
        self.assertIn("memory_search", names)

    def test_get_tool_returns_metadata(self):
        metadata = self.manager.get_tool("calculator")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["description"], "Calculate a simple arithmetic expression.")

    def test_execute_tool_calculator(self):
        result = self.manager.execute_tool("calculator", expression="2+2*3")
        self.assertEqual(result, "8")

    def test_execute_tool_system_info(self):
        result = self.manager.execute_tool("system_info")
        self.assertIn("platform:", result)
        self.assertIn("python_version:", result)

    def test_execute_tool_memory_search(self):
        self.manager.execute_tool("memory_save", text="Jarvis is a memory test", category="note")
        result = self.manager.execute_tool("memory_search", query="Jarvis")
        self.assertIn("Jarvis is a memory test", result)

    def test_execute_tool_missing_tool_raises(self):
        with self.assertRaises(ToolNotFoundError):
            self.manager.execute_tool("unknown_tool")

    def test_get_tool_missing_returns_none(self):
        self.assertIsNone(self.manager.get_tool("unknown_tool"))


if __name__ == "__main__":
    unittest.main()
