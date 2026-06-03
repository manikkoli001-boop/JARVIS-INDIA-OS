import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.decorator import tool
from core.memory.memory_ranker import MemoryRanker
from core.memory.memory_store import MemoryStore, VALID_CATEGORIES
from core.memory.memory_summarizer import MemorySummarizer

logger = logging.getLogger(__name__)


class MemoryManager:
    """Memory engine manager for Jarvis India OS."""

    def __init__(self, db_path: Optional[Path] = None):
        self.store = MemoryStore(db_path=db_path)
        self.short_term_memories: List[Dict[str, Any]] = []
        self.ranker = MemoryRanker()
        self.summarizer = MemorySummarizer()
        logger.info("MemoryManager initialized with database %s", self.store.db_path)

    def save_memory(self, text: str, category: str, importance: Optional[float] = None) -> Dict[str, Any]:
        importance = importance if importance is not None else self.ranker.compute_importance(text)
        logger.debug("Saving memory text=%s category=%s importance=%s", text, category, importance)
        return self.store.save_memory(text=text, category=category, importance=importance)

    def remember_short_term(self, text: str, category: str = "conversation", importance: Optional[float] = None) -> Dict[str, Any]:
        importance = importance if importance is not None else self.ranker.compute_importance(text)
        memory = {
            "id": len(self.short_term_memories) + 1,
            "text": text,
            "category": category,
            "importance": importance,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.short_term_memories.insert(0, memory)
        return memory

    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        logger.debug("Searching memory query=%s", query)
        long_term = self.store.search_memory(query)
        short_term = [m for m in self.short_term_memories if query.lower() in str(m["text"]).lower()]
        combined = short_term + long_term
        return self.ranker.rank_memories(query, combined)

    def list_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        logger.debug("Listing recent memories limit=%s", limit)
        recent = self.store.list_recent_memories(limit)
        short_term = self.short_term_memories[:max(0, limit - len(recent))]
        return short_term + recent

    def delete_memory(self, memory_id: int) -> bool:
        logger.debug("Deleting memory id=%s", memory_id)
        return self.store.delete_memory(memory_id)

    @staticmethod
    def validate_category(category: str) -> str:
        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. Valid categories are: {', '.join(sorted(VALID_CATEGORIES))}"
            )
        return category


memory_manager = MemoryManager()


@tool(name="memory_save", description="Save a memory entry with text and category.")
def memory_save(text: str, category: str = "note") -> str:
    category = MemoryManager.validate_category(category)
    record = memory_manager.save_memory(text=text, category=category)
    return f"Memory saved: id={record['id']} category={record['category']} created_at={record['created_at']}"


@tool(name="memory_search", description="Search memory entries by keyword.")
def memory_search(query: str) -> str:
    results = memory_manager.search_memory(query)
    if not results:
        return f"No memories found for '{query}'."
    return "\n".join(
        f"[{item['id']}] {item['category']} ({item['created_at']}): {item['text']}" for item in results
    )


@tool(name="memory_recent", description="List the most recent memory entries.")
def memory_recent(limit: int = 5) -> str:
    items = memory_manager.list_recent_memories(limit)
    if not items:
        return "No memories stored yet."
    return "\n".join(
        f"[{item['id']}] {item['category']} ({item['created_at']}): {item['text']}" for item in items
    )


@tool(name="memory_delete", description="Delete a memory entry by id.", sensitive=True, permission="admin")
def memory_delete(memory_id: int) -> str:
    deleted = memory_manager.delete_memory(memory_id)
    return "Memory deleted." if deleted else f"Memory id={memory_id} not found."
