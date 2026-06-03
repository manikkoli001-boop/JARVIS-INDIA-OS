import tempfile
import unittest
from pathlib import Path

from core import tool_audit
from core.tool_manager import ToolManager


class ToolSafeguardTest(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.audit_path = Path(self.temp_dir.name) / "tool_audit.jsonl"
        tool_audit._AUDIT_LOG_PATH = self.audit_path
        tool_audit.AUDIT_LOG.clear()
        if self.audit_path.exists():
            self.audit_path.unlink()
        self.manager = ToolManager()

    def tearDown(self):
        tool_audit.AUDIT_LOG.clear()
        self.temp_dir.cleanup()

    def test_sensitive_tool_requires_confirm(self):
        result = self.manager.execute_tool("system_shutdown")
        self.assertIn("requires confirm=True", result)
        recent = tool_audit.recent(1)
        self.assertEqual(len(recent), 1)
        self.assertFalse(recent[0]["allowed"])
        self.assertEqual(recent[0]["permission"], "admin")

    def test_sensitive_tool_with_confirm_and_admin_role_executes(self):
        result = self.manager.execute_tool("system_shutdown", confirm=True, actor_role="admin")
        self.assertIn("blocked by safe mode", result.lower())
        recent = tool_audit.recent(1)
        self.assertTrue(recent[0]["allowed"])
        self.assertEqual(recent[0]["actor_role"], "admin")

    def test_non_sensitive_tool_executes_and_audited(self):
        result = self.manager.execute_tool("calculator", expression="1+1")
        self.assertEqual(result, "2")
        recent = tool_audit.recent(1)
        self.assertTrue(recent[0]["allowed"])
        self.assertEqual(recent[0]["event"], "execute")

    def test_audit_entries_persist_to_disk_and_reload(self):
        self.manager.execute_tool("calculator", expression="3+4")
        self.assertTrue(self.audit_path.exists())
        self.assertGreater(self.audit_path.stat().st_size, 0)

        tool_audit.AUDIT_LOG.clear()
        reloaded = tool_audit.recent(1)
        self.assertEqual(len(reloaded), 1)
        self.assertEqual(reloaded[0]["tool"], "calculator")
        self.assertEqual(reloaded[0]["result"], "7")


if __name__ == "__main__":
    unittest.main()
