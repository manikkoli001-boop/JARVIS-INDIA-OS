import os
import platform
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.actions.close_app import close_app
from core.actions.open_app import open_app
from core.actions.open_file import open_file
from core.actions.open_folder import open_folder


class ActionFileTests(unittest.TestCase):

    @patch("core.actions.open_app.os.path.isfile", return_value=True)
    @patch("core.actions.open_app.os.startfile")
    def test_open_app_with_path_on_windows(self, mock_startfile, mock_isfile):
        with patch("platform.system", return_value="Windows"):
            result = open_app("C:\\Program Files\\app.exe")
        self.assertIn("Opening", result)
        mock_startfile.assert_called_once()

    @patch("core.actions.open_app.os.path.isfile", return_value=False)
    @patch("core.actions.open_app.subprocess.Popen")
    def test_open_app_by_name(self, mock_popen, mock_isfile):
        with patch("platform.system", return_value="Linux"):
            result = open_app("gedit")
        self.assertIn("Attempting to open", result)
        mock_popen.assert_called_once()

    @patch("core.actions.close_app.subprocess.run")
    def test_close_app_without_force(self, mock_run):
        with patch("platform.system", return_value="linux"):
            result = close_app("gedit")
        self.assertIn("Attempted to close", result)
        mock_run.assert_called_once()

    @patch("core.actions.open_file.Path.exists", return_value=True)
    @patch("core.actions.open_file.os.startfile")
    def test_open_file_windows(self, mock_startfile, mock_exists):
        with patch("platform.system", return_value="Windows"):
            result = open_file("C:\\test.txt")
        self.assertIn("Opening file", result)
        mock_startfile.assert_called_once()

    @patch("core.actions.open_folder.Path.is_dir", return_value=True)
    @patch("core.actions.open_folder.os.startfile")
    def test_open_folder_windows(self, mock_startfile, mock_is_dir):
        with patch("platform.system", return_value="Windows"):
            result = open_folder("C:\\Downloads")
        self.assertIn("Opening folder", result)
        mock_startfile.assert_called_once()


if __name__ == "__main__":
    unittest.main()
