import textwrap
from typing import Dict, List


class MemorySummarizer:
    """Summarize memory entries into concise context."""

    def summarize(self, memories: List[Dict[str, object]], limit: int = 3) -> str:
        if not memories:
            return "No memories to summarize."

        summaries = []
        for memory in memories[:limit]:
            text = str(memory.get("text", ""))
            summary = self._summarize_text(text)
            summaries.append(f"- {summary}")

        if len(memories) > limit:
            summaries.append(f"...and {len(memories) - limit} more memories.")

        return "\n".join(summaries)

    def _summarize_text(self, text: str) -> str:
        if len(text) <= 120:
            return text.strip()
        return textwrap.shorten(text, width=120, placeholder="...")
