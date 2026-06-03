import unittest
from unittest.mock import MagicMock

from core.voice_runtime import VoiceAssistant


class VoiceRuntimeTest(unittest.TestCase):

    def setUp(self):
        self.assistant = VoiceAssistant()
        self.assistant.speak = MagicMock()
        self.assistant.listen = MagicMock(return_value="")

    def test_wake_word_detection(self):
        self.assertTrue(self.assistant.is_wake_word("Hey Jarvis"))
        self.assertTrue(self.assistant.is_wake_word("jarvis"))
        self.assertFalse(self.assistant.is_wake_word("Hello world"))

    def test_extract_command_removes_wake_word(self):
        command = self.assistant.extract_command("Jarvis calculate 2+2")
        self.assertEqual(command, "calculate 2+2")

    def test_handle_help_command(self):
        response = self.assistant.handle_command("help")
        self.assertEqual(response["tool"], "help")
        self.assertIn("help", response["result"].lower())

    def test_handle_tools_command(self):
        response = self.assistant.handle_command("tools")
        self.assertEqual(response["tool"], "tools")
        self.assertIn("calculator", response["result"])

    def test_handle_memory_command(self):
        response = self.assistant.handle_command("memory")
        self.assertEqual(response["tool"], "memory")
        self.assertIn("recent memories", response["result"].lower())

    def test_handle_unknown_command(self):
        response = self.assistant.handle_command("tell me a joke")
        self.assertEqual(response["tool"], None)
        self.assertEqual(response["intent"], "unknown")

    def test_handle_exit_command(self):
        response = self.assistant.handle_command("exit")
        self.assertEqual(response["tool"], "exit")
        self.assertEqual(response["intent"], "exit")


if __name__ == "__main__":
    unittest.main()
