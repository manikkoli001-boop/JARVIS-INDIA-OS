import unittest
from core.tool_manager import ToolManager, ToolNotFoundError


class ToolManagerExtendedTest(unittest.TestCase):

    def setUp(self):
        self.manager = ToolManager()

    def test_get_tool_metadata(self):
        metadata = self.manager.get_tool_metadata("calculator")
        self.assertIsNotNone(metadata)
        self.assertIn("description", metadata)

    def test_execute_tool_missing_arguments_handles_error(self):
        with self.assertRaises(TypeError):
            self.manager.execute_tool("calculator")

    def test_get_tool_returns_none_for_unknown_tool(self):
        self.assertIsNone(self.manager.get_tool("nonexistent_tool"))


if __name__ == "__main__":
    unittest.main()
