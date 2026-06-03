import unittest

from core.memory.memory_ranker import MemoryRanker


class MemoryRankerTest(unittest.TestCase):

    def setUp(self):
        self.ranker = MemoryRanker()
        self.memories = [
            {"text": "Buy milk and eggs", "importance": 0.6},
            {"text": "Finish urgent report", "importance": 0.9},
            {"text": "Call Alice tomorrow", "importance": 0.4},
        ]

    def test_rank_memories_by_query(self):
        ranked = self.ranker.rank_memories("urgent", self.memories)
        self.assertEqual(ranked[0]["text"], "Finish urgent report")

    def test_compute_importance_with_keywords(self):
        score = self.ranker.compute_importance("This is an urgent task with a deadline")
        self.assertGreaterEqual(score, 0.8)


if __name__ == "__main__":
    unittest.main()
