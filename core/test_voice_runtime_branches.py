import unittest
from unittest.mock import MagicMock, patch

import core.voice_runtime as voice_runtime
from core.voice_runtime import VoiceAssistant


class VoiceRuntimeBranchesTest(unittest.TestCase):

    def setUp(self):
        self.mock_engine = MagicMock()
        self.patcher = patch("core.voice_runtime.pyttsx3.init", return_value=self.mock_engine)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.assistant = VoiceAssistant()
        self.assistant.speak = MagicMock()
        self.assistant.recognizer.adjust_for_ambient_noise = MagicMock()

    def test_speak_empty_does_nothing(self):
        self.assistant.speak("")
        self.mock_engine.say.assert_not_called()

    def test_is_wake_word_detects_jarvis(self):
        self.assertTrue(self.assistant.is_wake_word("Hey Jarvis, open chrome"))
        self.assertFalse(self.assistant.is_wake_word("Hello there"))

    def test_extract_command_removes_wake_word(self):
        self.assertEqual(self.assistant.extract_command("Jarvis open browser"), "open browser")

    def test_help_tools_memory_commands(self):
        self.assistant.tool_manager.list_tools = MagicMock(return_value=["calculator"])
        self.assertIn("help", self.assistant.help_text().lower())
        self.assertIn("calculator", self.assistant.list_tools())

    @patch("core.voice_runtime.memory_manager.list_recent_memories", return_value=[])
    def test_memory_summary_no_memories(self, mock_recent):
        self.assertEqual(self.assistant.memory_summary(), "No memories are stored yet.")

    @patch("core.voice_runtime.memory_manager.list_recent_memories")
    def test_memory_summary_with_memories(self, mock_recent):
        mock_recent.return_value = [{"id": 1, "category": "note", "text": "Test text"}]
        self.assertIn("Recent memories", self.assistant.memory_summary())

    def test_handle_command_exit(self):
        result = self.assistant.handle_command("exit")
        self.assertEqual(result["tool"], "exit")

    def test_handle_command_unknown_route(self):
        self.assistant.router.route = MagicMock(return_value={"tool": None, "intent": "unknown", "result": "unknown"})
        result = self.assistant.handle_command("tell me a joke")
        self.assertEqual(result["intent"], "unknown")

    @patch("core.voice_runtime.sr.Microphone")
    def test_listen_wait_timeout_returns_empty(self, mock_microphone):
        recognizer = self.assistant.recognizer
        recognizer.listen = MagicMock(side_effect=voice_runtime.sr.WaitTimeoutError)
        mock_microphone.return_value.__enter__.return_value = MagicMock()
        self.assertEqual(self.assistant.listen(), "")

    @patch("core.voice_runtime.sr.Microphone")
    def test_listen_unknown_value_speaks_error(self, mock_microphone):
        recognizer = self.assistant.recognizer
        recognizer.listen = MagicMock(return_value=MagicMock())
        recognizer.recognize_google = MagicMock(side_effect=voice_runtime.sr.UnknownValueError)
        mock_microphone.return_value.__enter__.return_value = MagicMock()
        self.assertEqual(self.assistant.listen(), "")
        self.assistant.speak.assert_called_once()

    @patch("core.voice_runtime.sr.Microphone")
    def test_listen_request_error_speaks_unavailable(self, mock_microphone):
        recognizer = self.assistant.recognizer
        recognizer.listen = MagicMock(return_value=MagicMock())
        recognizer.recognize_google = MagicMock(side_effect=voice_runtime.sr.RequestError("service"))
        mock_microphone.return_value.__enter__.return_value = MagicMock()
        self.assertEqual(self.assistant.listen(), "")
        self.assistant.speak.assert_called_once()

    @patch("core.voice_runtime.sr.Microphone")
    def test_listen_generic_exception_speaks_error(self, mock_microphone):
        recognizer = self.assistant.recognizer
        recognizer.listen = MagicMock(side_effect=ValueError("oops"))
        mock_microphone.return_value.__enter__.return_value = MagicMock()
        self.assertEqual(self.assistant.listen(), "")
        self.assistant.speak.assert_called_once()

    @patch("core.voice_runtime.time.sleep", return_value=None)
    @patch("core.voice_runtime.sr.Microphone")
    def test_run_exit_flow(self, mock_microphone, mock_sleep):
        self.assistant.listen = MagicMock(side_effect=["Jarvis exit"])
        self.assistant.speak = MagicMock()
        self.assistant.run()
        self.assistant.speak.assert_any_call("Goodbye.")


if __name__ == "__main__":
    unittest.main()
