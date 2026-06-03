import unittest
from unittest.mock import MagicMock, patch

from core.runtime.jarvis_runtime import JarvisRuntime


class JarvisRuntimeRunTest(unittest.TestCase):

    @patch("core.runtime.jarvis_runtime.WakeWordDetector")
    @patch("core.runtime.jarvis_runtime.time.sleep", return_value=None)
    def test_run_processes_commands_and_stops(self, mock_sleep, mock_detector):
        mock_detector_instance = mock_detector.return_value
        mock_detector_instance.should_start_session.side_effect = [True, True]
        mock_detector_instance.extract_command.side_effect = ["open browser", "exit"]

        runtime = JarvisRuntime(agent=MagicMock())
        runtime.listen = MagicMock(side_effect=["Jarvis open browser", "Jarvis exit"])
        runtime.speak = MagicMock()

        runtime.run()

        self.assertFalse(runtime._running)
        self.assertEqual(runtime.listen.call_count, 2)


if __name__ == "__main__":
    unittest.main()
