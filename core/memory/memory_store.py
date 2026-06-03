import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_FILENAME = "jarvis_memory.db"
VALID_CATEGORIES = {"conversation", "task", "project", "reminder", "note"}


class MemoryStore:
    """Low-level SQLite memory store for Jarvis India OS."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path(__file__).resolve().parent / DB_FILENAME
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    category TEXT NOT NULL,
                    importance REAL NOT NULL DEFAULT 0.5,
                    created_at TEXT NOT NULL
                )
                """
            )
        self._ensure_importance_column()

    def _ensure_importance_column(self) -> None:
        cursor = self.connection.execute("PRAGMA table_info(memories)")
        columns = [row[1] for row in cursor.fetchall()]
        if "importance" not in columns:
            with self.connection:
                self.connection.execute("ALTER TABLE memories ADD COLUMN importance REAL NOT NULL DEFAULT 0.5")

    def _validate_category(self, category: str) -> None:
        if category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Valid categories: {', '.join(sorted(VALID_CATEGORIES))}")

    def save_memory(self, text: str, category: str, importance: float = 0.5) -> Dict[str, Any]:
        self._validate_category(category)
        created_at = datetime.utcnow().isoformat(sep=" ", timespec="microseconds")
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO memories (text, category, importance, created_at) VALUES (?, ?, ?, ?)",
                (text, category, importance, created_at),
            )
            memory_id = cursor.lastrowid
        return {
            "id": memory_id,
            "text": text,
            "category": category,
            "importance": importance,
            "created_at": created_at,
        }

    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        query_phrase = f"%{query}%"
        cursor = self.connection.execute(
            "SELECT * FROM memories WHERE text LIKE ? OR category LIKE ? ORDER BY created_at DESC, id DESC",
            (query_phrase, query_phrase),
        )
        return [dict(row) for row in cursor.fetchall()]

    def list_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = self.connection.execute(
            "SELECT * FROM memories ORDER BY created_at DESC, id DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def delete_memory(self, memory_id: int) -> bool:
        with self.connection:
            cursor = self.connection.execute(
                "DELETE FROM memories WHERE id = ?",
                (memory_id,),
            )
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()
