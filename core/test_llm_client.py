import json
import unittest
from unittest.mock import patch
from urllib.error import URLError

from core.llm_client import OllamaClient


class OllamaClientTest(unittest.TestCase):

    def test_parse_openai_style_response(self):
        client = OllamaClient()
        response = {
            "choices": [
                {"message": {"content": "{\"tool\": null, \"parameters\": {}, \"reply\": \"Hello\"}"}}
            ]
        }
        self.assertEqual(client._parse_response(response), '{"tool": null, "parameters": {}, "reply": "Hello"}')

    def test_parse_output_list_response(self):
        client = OllamaClient()
        response = {
            "choices": [
                {"output": [{"content": "{\"tool\": \"calculator\", \"parameters\": {\"expression\": \"2+2\"}, \"reply\": \"Calculating\"}"}]}
            ]
        }
        self.assertEqual(client._parse_response(response), '{"tool": "calculator", "parameters": {"expression": "2+2"}, "reply": "Calculating"}')

    @patch.object(OllamaClient, "_request", side_effect=URLError("Connection refused"))
    def test_query_fallback_response_when_service_unavailable(self, mocked_request):
        client = OllamaClient()
        messages = [{"role": "user", "content": "Hello"}]
        result = client.query(messages)
        self.assertIn("I could not reach the Ollama model", result)
        self.assertIn("Hello", result)


if __name__ == "__main__":
    unittest.main()
