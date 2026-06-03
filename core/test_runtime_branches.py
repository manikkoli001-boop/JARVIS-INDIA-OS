import unittest
from unittest.mock import MagicMock, patch

from core.runtime.jarvis_runtime import JarvisRuntime
from core.runtime.jarvis_runtime import sr as runtime_sr


class RuntimeBranchesTest(unittest.TestCase):

    @patch("core.runtime.jarvis_runtime.pyttsx3.init")
    def setUp(self, mock_init):
        self.mock_engine = MagicMock()
        mock_init.return_value = self.mock_engine
        self.runtime = JarvisRuntime(agent=MagicMock())
        self.runtime.speak = MagicMock()
        self.runtime.recognizer.adjust_for_ambient_noise = MagicMock()

    def test_process_command_exit(self):
        self.runtime._running = True
        result = self.runtime._process_command("exit")
        self.assertEqual(result, "Goodbye.")
        self.assertFalse(self.runtime._running)

    def test_process_command_agent_dict(self):
        agent = MagicMock()
        agent.run_task.return_value = {"result": "done"}
        runtime = JarvisRuntime(agent=agent)
        self.assertEqual(runtime._process_command("anything"), "done")

    @patch("core.runtime.jarvis_runtime.sr.Microphone")
    def test_listen_wait_timeout(self, mock_microphone):
        recognizer = self.runtime.recognizer
        recognizer.listen = MagicMock(side_effect=runtime_sr.WaitTimeoutError)
        mock_microphone.return_value.__enter__.return_value = MagicMock()
        self.assertEqual(self.runtime.listen(), "")

    @patch("core.runtime.jarvis_runtime.sr.Microphone")
    def test_listen_unknown_value(self, mock_microphone):
        recognizer = self.runtime.recognizer
        recognizer.listen = MagicMock(return_value=MagicMock())
        recognizer.recognize_google = MagicMock(side_effect=runtime_sr.UnknownValueError)
        mock_microphone.return_value.__enter__.return_value = MagicMock()
        self.assertEqual(self.runtime.listen(), "")
        self.runtime.speak.assert_called_once()

    @patch("core.runtime.jarvis_runtime.sr.Microphone")
    def test_listen_request_error(self, mock_microphone):
        recognizer = self.runtime.recognizer
        recognizer.listen = MagicMock(return_value=MagicMock())
        recognizer.recognize_google = MagicMock(side_effect=runtime_sr.RequestError("error"))
        mock_microphone.return_value.__enter__.return_value = MagicMock()
        self.assertEqual(self.runtime.listen(), "")
        self.runtime.speak.assert_called_once()

    @patch("core.runtime.jarvis_runtime.sr.Microphone")
    def test_listen_exception(self, mock_microphone):
        recognizer = self.runtime.recognizer
        recognizer.listen = MagicMock(side_effect=ValueError("boom"))
        mock_microphone.return_value.__enter__.return_value = MagicMock()
        self.assertEqual(self.runtime.listen(), "")
        self.runtime.speak.assert_called_once()


if __name__ == "__main__":
    unittest.main()
