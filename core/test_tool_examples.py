import unittest
from core.tool_examples import calculator, system_info, memory_search


class ToolExamplesTest(unittest.TestCase):

    def test_calculator_addition(self):
        self.assertEqual(calculator("2+3*4"), "14")

    def test_calculator_invalid_expression(self):
        with self.assertRaises(ValueError):
            calculator("rm -rf /")

    def test_system_info_returns_string(self):
        info = system_info()
        self.assertIn("platform", info)
        self.assertIn("python_version", info)

    def test_memory_search_returns_message(self):
        result = memory_search("Jarvis")
        self.assertIn("Jarvis India OS", result)


if __name__ == "__main__":
    unittest.main()
