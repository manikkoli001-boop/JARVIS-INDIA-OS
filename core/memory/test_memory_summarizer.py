import unittest

from core.memory.memory_summarizer import MemorySummarizer


class MemorySummarizerTest(unittest.TestCase):

    def setUp(self):
        self.summarizer = MemorySummarizer()

    def test_summarize_short_memories(self):
        memories = [{"text": "Jarvis is learning to reason."}]
        summary = self.summarizer.summarize(memories)
        self.assertIn("Jarvis is learning to reason", summary)

    def test_summarize_long_memories_truncates(self):
        memories = [{"text": "A" * 200}]
        summary = self.summarizer.summarize(memories)
        self.assertTrue(summary.endswith("..."))


if __name__ == "__main__":
    unittest.main()
