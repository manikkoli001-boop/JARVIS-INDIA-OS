import unittest

from core.llm_client import OllamaClient


class LLmClientParseExtendedTest(unittest.TestCase):

    def setUp(self):
        self.client = OllamaClient()

    def test_parse_response_choice_content(self):
        response = {"choices": [{"message": {"content": "hello"}}]}
        self.assertEqual(self.client._parse_response(response), "hello")

    def test_parse_response_choice_direct_content(self):
        response = {"choices": [{"content": "world"}]}
        self.assertEqual(self.client._parse_response(response), "world")

    def test_parse_response_output_list(self):
        response = {"choices": [{"output": [{"content": "output text"}]}]}
        self.assertEqual(self.client._parse_response(response), "output text")

    def test_parse_response_top_level_output(self):
        response = {"output": [{"content": "outer text"}]}
        self.assertEqual(self.client._parse_response(response), "outer text")

    def test_parse_response_fallback_to_raw(self):
        response = "some raw text"
        self.assertEqual(self.client._parse_response(response), "some raw text")


if __name__ == "__main__":
    unittest.main()
