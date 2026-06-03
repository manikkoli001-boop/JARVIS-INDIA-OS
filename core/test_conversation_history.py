import unittest

from core.conversation_history import ConversationHistory


class ConversationHistoryTest(unittest.TestCase):

    def setUp(self):
        self.history = ConversationHistory(max_entries=3)

    def test_add_user_and_assistant_messages(self):
        self.history.add_user_message("Hello")
        self.history.add_assistant_message("Hi there")
        self.assertEqual(len(self.history.messages), 2)
        self.assertEqual(self.history.messages[0]["role"], "user")
        self.assertEqual(self.history.messages[1]["role"], "assistant")

    def test_recent_messages_limit(self):
        self.history.add_user_message("A")
        self.history.add_assistant_message("B")
        self.history.add_user_message("C")
        self.history.add_assistant_message("D")
        self.assertEqual(len(self.history.recent_messages()), 3)
        self.assertEqual(self.history.recent_messages()[0]["content"], "B")

    def test_as_prompt_formats_messages(self):
        self.history.add_user_message("Hello")
        self.history.add_assistant_message("Response")
        prompt = self.history.as_prompt()
        self.assertIn("User: Hello", prompt)
        self.assertIn("Assistant: Response", prompt)


if __name__ == "__main__":
    unittest.main()
