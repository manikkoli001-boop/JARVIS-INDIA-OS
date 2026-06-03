import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_AUDIT_LOCK = threading.RLock()
_AUDIT_LOG_PATH = Path(os.environ.get("JARVIS_AUDIT_LOG_PATH", "logs/tool_audit.jsonl"))
AUDIT_LOG: List[Dict[str, Any]] = []


def _resolve_audit_path(path: Optional[str] = None) -> Path:
    candidate = Path(path) if path is not None else _AUDIT_LOG_PATH
    return candidate.expanduser()


def _sanitize_parameters(parameters: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in parameters.items() if key not in {"confirm", "__actor_role", "__user"}}


def _ensure_audit_directory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _load_audit_entries(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    entries: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed audit log line in %s", path)
                    continue
                if isinstance(entry, dict):
                    entries.append(entry)
    except OSError as exc:
        logger.exception("Failed to read audit log file %s: %s", path, exc)
    return entries


def _append_audit_entry(path: Path, entry: Dict[str, Any]) -> None:
    _ensure_audit_directory(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")


def _initialize_audit_log() -> None:
    with _AUDIT_LOCK:
        if AUDIT_LOG:
            return
        AUDIT_LOG.extend(_load_audit_entries(_resolve_audit_path()))


def record_attempt(
    tool_name: str,
    parameters: Dict[str, Any],
    allowed: bool,
    result: Optional[Any] = None,
    error: Optional[str] = None,
    user: str = "system",
    event: str = "execute",
    actor_role: str = "system",
    sensitive: bool = False,
    permission: str = "user",
    reason: Optional[str] = None,
) -> None:
    entry = {
        "timestamp": time.time(),
        "event": event,
        "tool": tool_name,
        "user": user,
        "actor_role": actor_role,
        "parameters": _sanitize_parameters(dict(parameters)),
        "allowed": bool(allowed),
        "sensitive": bool(sensitive),
        "permission": permission,
        "reason": reason,
        "result": str(result) if result is not None else None,
        "error": error,
    }

    path = _resolve_audit_path()
    with _AUDIT_LOCK:
        AUDIT_LOG.append(entry)
        try:
            _append_audit_entry(path, entry)
        except OSError as exc:
            logger.exception("Failed to append audit log entry to %s: %s", path, exc)


def recent(limit: int = 10) -> List[Dict[str, Any]]:
    with _AUDIT_LOCK:
        if not AUDIT_LOG:
            _initialize_audit_log()
        return list(reversed(AUDIT_LOG[-limit:]))


_initialize_audit_log()
