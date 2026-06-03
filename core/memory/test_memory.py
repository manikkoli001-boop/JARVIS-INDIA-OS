import os
import tempfile
import unittest
from pathlib import Path

from core.memory.memory_manager import MemoryManager


class MemoryEngineTest(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "jarvis_memory_test.db"
        self.manager = MemoryManager(db_path=self.db_path)

    def tearDown(self):
        self.manager.store.close()
        self.temp_dir.cleanup()

    def test_save_and_search_memory(self):
        result = self.manager.save_memory("Remember to check logs", "task")
        self.assertEqual(result["category"], "task")
        self.assertIn("Remember to check logs", result["text"])

        search = self.manager.search_memory("check")
        self.assertEqual(len(search), 1)
        self.assertEqual(search[0]["category"], "task")

    def test_list_recent_memories_respects_limit(self):
        for value in range(1, 6):
            self.manager.save_memory(f"Memory {value}", "note")

        recent = self.manager.list_recent_memories(limit=3)
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[0]["text"], "Memory 5")

    def test_delete_memory_removes_entry(self):
        created = self.manager.save_memory("Delete me", "reminder")
        deleted = self.manager.delete_memory(created["id"])
        self.assertTrue(deleted)

        search = self.manager.search_memory("Delete me")
        self.assertEqual(len(search), 0)

    def test_invalid_category_raises(self):
        with self.assertRaises(ValueError):
            self.manager.save_memory("Bad category", "unsupported")

    def test_save_with_automatic_timestamp(self):
        created = self.manager.save_memory("Timestamp me", "note")
        self.assertIn("created_at", created)
        self.assertIsInstance(created["created_at"], str)


if __name__ == "__main__":
    unittest.main()
