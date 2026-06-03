from typing import Dict, List


class ConversationHistory:
    """Store a running conversation history for Jarvis AI."""

    def __init__(self, max_entries: int = 50):
        self.max_entries = max_entries
        self.messages: List[Dict[str, str]] = []

    def add_user_message(self, text: str) -> None:
        self._append_message("user", text)

    def add_assistant_message(self, text: str) -> None:
        self._append_message("assistant", text)

    def recent_messages(self, limit: int = 10) -> List[Dict[str, str]]:
        return self.messages[-limit:]

    def _append_message(self, role: str, text: str) -> None:
        self.messages.append({"role": role, "content": text})
        if len(self.messages) > self.max_entries:
            self.messages = self.messages[-self.max_entries:]

    def as_prompt(self, limit: int = 10) -> str:
        lines = []
        for message in self.recent_messages(limit):
            role = message["role"].capitalize()
            lines.append(f"{role}: {message['content']}")
        return "\n".join(lines)
