import os
import unittest
from unittest.mock import MagicMock, patch

from core.actions.open_website import open_website
from core.actions.search_web import search_web
from core.actions.system_control import brightness_control, system_restart, system_shutdown, system_sleep, volume_control


class ActionsTest(unittest.TestCase):

    @patch("webbrowser.open")
    def test_open_website(self, mock_open):
        result = open_website("example.com")
        self.assertIn("Opening website", result)
        mock_open.assert_called_once()

    @patch("webbrowser.open")
    def test_search_web(self, mock_open):
        result = search_web("weather today")
        self.assertIn("Searching the web for", result)
        mock_open.assert_called_once()

    @patch("core.actions.system_control.subprocess.run")
    def test_system_shutdown_requires_confirm(self, mock_run):
        result = system_shutdown(confirm=False)
        self.assertIn("Confirm shutdown", result)
        mock_run.assert_not_called()

    @patch("core.actions.system_control.subprocess.run")
    def test_system_restart_requires_confirm(self, mock_run):
        result = system_restart(confirm=False)
        self.assertIn("Confirm restart", result)
        mock_run.assert_not_called()

    @patch("core.actions.system_control.subprocess.run")
    def test_volume_control_confirm(self, mock_run):
        result = volume_control(level=50, confirm=True)
        self.assertIn("Setting volume", result)
        mock_run.assert_not_called()

    @patch("core.actions.system_control.subprocess.run")
    def test_brightness_control_confirm(self, mock_run):
        result = brightness_control(level=70, confirm=True)
        self.assertIn("Setting brightness", result)
        mock_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
