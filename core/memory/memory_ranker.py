import re
from typing import Dict, List


class MemoryRanker:
    """Rank memories based on relevance, recency and importance."""

    def rank_memories(self, query: str, memories: List[Dict[str, object]]) -> List[Dict[str, object]]:
        if not query or not memories:
            return memories

        normalized = query.lower()
        ranked = []
        for memory in memories:
            score = 0.0
            text = str(memory.get("text", "")).lower()
            if normalized in text:
                score += 2.0
            for word in normalized.split():
                if word and word in text:
                    score += 0.5
            importance = float(memory.get("importance", 0.5) or 0.5)
            score += importance
            score += max(0.0, 1.0 - min(1.0, len(text) / 200.0))
            ranked.append((score, memory))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in ranked]

    def compute_importance(self, text: str) -> float:
        text = str(text).strip().lower()
        if not text:
            return 0.1
        importance = 0.5
        if any(keyword in text for keyword in ["deadline", "urgent", "important", "remember", "priority"]):
            importance += 0.4
        if len(text) > 120:
            importance += 0.1
        return min(1.0, importance)
