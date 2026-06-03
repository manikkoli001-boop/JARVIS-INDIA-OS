import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from core.llm_client import OllamaClient


class LLMClientExtendedTest(unittest.TestCase):

    @patch("core.llm_client.urlopen")
    def test_request_parses_response(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"choices": [{"message": {"content": "hello"}}]}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response
        client = OllamaClient()
        output = client._request({"model": client.model})
        self.assertIsInstance(output, dict)

    @patch("core.llm_client.urlopen", side_effect=URLError("Connection refused"))
    def test_query_handles_connection_error(self, mock_urlopen):
        client = OllamaClient()
        result = client.query([{"role": "user", "content": "test"}])
        self.assertIn("I could not reach the Ollama model", result)

    @patch("core.llm_client.urlopen")
    def test_parse_response_handles_nonstandard_output(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"{\"output\": [{\"content\": \"test\"}]}"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        client = OllamaClient()
        output = client._request({"model": client.model})
        self.assertEqual(output["output"][0]["content"], "test")


if __name__ == "__main__":
    unittest.main()
