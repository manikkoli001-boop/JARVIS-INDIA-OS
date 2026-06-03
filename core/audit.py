import json
import time
from pathlib import Path
from typing import Any, Dict, List

_AUDIT_PATH = Path("logs") / "audit.log"
_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)


class AuditLogger:
    """Simple audit logger that appends JSON lines to logs/audit.log and keeps in-memory records for tests."""

    def __init__(self):
        self._records: List[Dict[str, Any]] = []

    def record(self, event: str, tool: str, user: str = "system", parameters: Dict[str, Any] = None, result: Any = None, allowed: bool = True, sensitive: bool = False) -> None:
        parameters = parameters or {}
        rec = {
            "ts": time.time(),
            "event": event,
            "tool": tool,
            "user": user,
            "parameters": parameters,
            "result": str(result) if result is not None else None,
            "allowed": bool(allowed),
            "sensitive": bool(sensitive),
        }
        self._records.append(rec)
        try:
            with _AUDIT_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, default=str) + "\n")
        except Exception:
            # Never crash the tool manager because audit failed
            pass

    def recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self._records[-limit:])


_AUDIT = AuditLogger()


def get_audit_logger() -> AuditLogger:
    return _AUDIT
