import platform
import unittest
from unittest.mock import patch

from core.actions.system_control import (
    brightness_control,
    system_restart,
    system_sleep,
    system_shutdown,
    volume_control,
)


class SystemControlTests(unittest.TestCase):

    def test_shutdown_requires_confirmation(self):
        self.assertEqual(system_shutdown(), "Confirm shutdown by setting confirm=True.")

    @patch("core.actions.system_control.os.environ", {})
    @patch("core.actions.system_control.platform.system", return_value="windows")
    @patch("core.actions.system_control._windows_command")
    def test_shutdown_blocked_when_safe_mode_disabled(self, mock_cmd, _mock_platform, _mock_environ):
        self.assertIn("blocked by safe mode", system_shutdown(confirm=True).lower())
        mock_cmd.assert_not_called()

    @patch.dict("core.actions.system_control.os.environ", {"JARVIS_ALLOW_POWER_ACTIONS": "1"})
    @patch("core.actions.system_control.platform.system", return_value="windows")
    @patch("core.actions.system_control._windows_command")
    def test_shutdown_on_windows(self, mock_cmd, _mock_platform):
        self.assertEqual(system_shutdown(confirm=True), "System shutdown initiated.")
        mock_cmd.assert_called_once()

    def test_volume_control_requires_confirmation(self):
        self.assertEqual(volume_control(level=50), "Confirm volume change by setting confirm=True.")

    def test_volume_control_level_bounds(self):
        self.assertEqual(volume_control(level=101, confirm=True), "Volume level must be between 0 and 100.")
        self.assertEqual(volume_control(level=75, confirm=True), "Setting volume to 75%.")

    def test_brightness_control_invalid_level(self):
        self.assertEqual(brightness_control(level=-1, confirm=True), "Brightness level must be between 0 and 100.")
        self.assertEqual(brightness_control(change="up", confirm=True), "Adjusting brightness up.")

    @patch.dict("core.actions.system_control.os.environ", {"JARVIS_ALLOW_POWER_ACTIONS": "1"})
    @patch("core.actions.system_control.platform.system", return_value="linux")
    def test_restart_non_windows(self, mock_platform):
        self.assertEqual(system_restart(confirm=True), "System restart is not supported on this platform.")

    @patch.dict("core.actions.system_control.os.environ", {"JARVIS_ALLOW_POWER_ACTIONS": "1"})
    @patch("core.actions.system_control.platform.system", return_value="linux")
    def test_sleep_non_windows(self, mock_platform):
        self.assertEqual(system_sleep(confirm=True), "System sleep is not supported on this platform.")


if __name__ == "__main__":
    unittest.main()
