import unittest
from unittest.mock import MagicMock

from core.runtime.jarvis_runtime import JarvisRuntime


class JarvisRuntimeTest(unittest.TestCase):

    def setUp(self):
        self.mock_agent = MagicMock()
        self.mock_agent.run_task.return_value = {"result": "Done", "trace": []}
        self.runtime = JarvisRuntime(agent=self.mock_agent)

    def test_process_command_for_task(self):
        response = self.runtime._process_command("Open website example.com")
        self.assertEqual(response, "Done")
        self.mock_agent.run_task.assert_called_once_with("Open website example.com")

    def test_process_command_stops_on_exit(self):
        response = self.runtime._process_command("exit")
        self.assertEqual(response, "Goodbye.")
        self.assertFalse(self.runtime._running)


if __name__ == "__main__":
    unittest.main()
