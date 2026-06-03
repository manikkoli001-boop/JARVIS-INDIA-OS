import unittest
from unittest.mock import MagicMock

from core.voice_runtime import VoiceAssistant


class VoiceRuntimeExtendedTest(unittest.TestCase):

    def setUp(self):
        self.assistant = VoiceAssistant()
        self.assistant.speak = MagicMock()
        self.assistant.listen = MagicMock(return_value="")

    def test_help_command(self):
        response = self.assistant.handle_command("help")
        self.assertEqual(response["tool"], "help")
        self.assertIn("help", response["result"].lower())

    def test_tools_command(self):
        response = self.assistant.handle_command("tools")
        self.assertEqual(response["tool"], "tools")

    def test_memory_command(self):
        response = self.assistant.handle_command("memory")
        self.assertEqual(response["tool"], "memory")

    def test_unknown_command_fallback(self):
        response = self.assistant.handle_command("tell me a joke")
        self.assertEqual(response["tool"], None)
        self.assertEqual(response["intent"], "unknown")


if __name__ == "__main__":
    unittest.main()
