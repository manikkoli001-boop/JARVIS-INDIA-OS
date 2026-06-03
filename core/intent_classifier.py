import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    tool_name: Optional[str]
    intent: str
    confidence: float
    command: str
    parameters: Dict[str, object]


class IntentClassifier:
    """Simple intent classifier for command routing."""

    KNOWN_TOOLS = {
        "memory_save": [
            "remember", "save", "store", "note", "memo", "record", "add memory",
        ],
        "memory_search": [
            "find", "search", "recall", "lookup", "look up", "remembered", "search memory",
        ],
        "memory_recent": [
            "recent", "latest", "show memories", "list memories", "recent memories", "latest memories",
        ],
        "memory_delete": [
            "delete", "remove", "forget", "erase", "discard",
        ],
        "calculator": [
            "calculate", "what is", "what's", "compute", "sum", "subtract", "multiply", "divide", "plus", "minus",
        ],
        "system_info": [
            "system info", "system status", "system details", "environment", "platform", "python version", "runtime info",
        ],
    }

    def __init__(self) -> None:
        self.patterns: Dict[str, List[Pattern[str]]] = {
            tool: [re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE) for keyword in keywords]
            for tool, keywords in self.KNOWN_TOOLS.items()
        }

    def classify(self, command: str) -> IntentResult:
        normalized = command.strip()
        if not normalized:
            return IntentResult(None, "unknown", 0.0, command, {})

        scores: Dict[str, float] = {}
        for tool_name, patterns in self.patterns.items():
            score = 0.0
            for pattern in patterns:
                if pattern.search(normalized):
                    score += 1.0
            if tool_name in normalized.lower():
                score += 0.5
            scores[tool_name] = score
            logger.debug("Intent score for %s = %s", tool_name, score)

        best_tool = max(scores, key=scores.get)
        best_score = scores[best_tool]
        confidence = min(
            1.0,
            max(0.1, best_score / max(1.0, len(self.patterns[best_tool]) / 4.0)),
        )

        if best_score <= 0:
            logger.debug("No intent match for command '%s'", command)
            return IntentResult(None, "unknown", 0.0, command, {})

        parameters = self._extract_parameters(best_tool, normalized)
        logger.info("Classified command '%s' as '%s' with confidence %.2f", command, best_tool, confidence)
        return IntentResult(best_tool, best_tool, confidence, command, parameters)

    def _extract_parameters(self, tool_name: str, command: str) -> Dict[str, object]:
        lower = command.lower()
        if tool_name == "memory_save":
            category = self._find_category(command) or "note"
            return {"text": command.strip(), "category": category}
        if tool_name == "memory_search":
            return {"query": command.strip()}
        if tool_name == "memory_recent":
            limit = self._extract_number(command, default=5)
            return {"limit": limit}
        if tool_name == "memory_delete":
            memory_id = self._extract_number(command)
            return {"memory_id": memory_id} if memory_id is not None else {}
        if tool_name == "calculator":
            expression = self._extract_expression(command)
            return {"expression": expression}
        return {}

    def _find_category(self, command: str) -> Optional[str]:
        categories = ["conversation", "task", "project", "reminder", "note"]
        for category in categories:
            if re.search(rf"\b{re.escape(category)}\b", command, re.IGNORECASE):
                return category
        return None

    def _extract_number(self, command: str, default: Optional[int] = None) -> Optional[int]:
        match = re.search(r"\b(\d+)\b", command)
        if match:
            return int(match.group(1))
        return default

    def _extract_expression(self, command: str) -> str:
        command = re.sub(r"^(calculate|compute|what is|what's)\s*", "", command, flags=re.IGNORECASE)
        return command.strip()
