import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

from core import tool_audit
from core.decorator import TOOL_REGISTRY

logger = logging.getLogger(__name__)

_PERMISSION_HIERARCHY = {
    "guest": 0,
    "user": 1,
    "power": 2,
    "admin": 3,
    "system": 4,
}
_DEFAULT_ACTOR_ROLE = os.environ.get("JARVIS_DEFAULT_ACTOR_ROLE", "user").strip().lower() or "user"


def _normalize_role(role: Optional[str], hierarchy: Mapping[str, int]) -> str:
    normalized = _DEFAULT_ACTOR_ROLE if role is None else str(role).strip().lower()
    if not normalized:
        normalized = _DEFAULT_ACTOR_ROLE
    return normalized if normalized in hierarchy else "guest"


def _permission_rank(permission: str, hierarchy: Mapping[str, int]) -> int:
    return hierarchy.get(permission, -1)


def _permission_label(permission: str) -> str:
    return permission if permission else "user"


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    reason: str
    tool_name: str
    actor_role: str
    required_permission: str
    sensitive: bool
    confirm_required: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class SafetyEngine:
    """Central policy enforcement for tool and workflow execution."""

    def __init__(
        self,
        registry: Optional[Mapping[str, Dict[str, Any]]] = None,
        permission_hierarchy: Optional[Mapping[str, int]] = None,
    ):
        self.registry = registry or TOOL_REGISTRY
        self.permission_hierarchy = dict(permission_hierarchy or _PERMISSION_HIERARCHY)

    def get_tool_metadata(self, tool_name: str) -> Optional[Dict[str, Any]]:
        metadata = self.registry.get(tool_name)
        if metadata is None:
            return None
        return dict(metadata)

    def authorize(
        self,
        tool_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        actor_role: Optional[str] = None,
        user: str = "system",
    ) -> SafetyDecision:
        parameters = dict(parameters or {})
        metadata = self.get_tool_metadata(tool_name)
        normalized_actor_role = _normalize_role(actor_role, self.permission_hierarchy)

        if metadata is None:
            reason = f"Tool '{tool_name}' is not registered."
            decision = SafetyDecision(
                allowed=False,
                reason=reason,
                tool_name=tool_name,
                actor_role=normalized_actor_role,
                required_permission="unregistered",
                sensitive=False,
                confirm_required=False,
            )
            self._record_decision(decision, parameters, user)
            return decision

        required_permission = _permission_label(str(metadata.get("permission", "user")).strip().lower())
        sensitive = bool(metadata.get("sensitive", False))
        confirm_required = sensitive
        confirm_supplied = bool(parameters.get("confirm", False))

        if required_permission not in self.permission_hierarchy:
            reason = f"Tool '{tool_name}' is misconfigured with unknown permission '{required_permission}'."
            decision = SafetyDecision(
                allowed=False,
                reason=reason,
                tool_name=tool_name,
                actor_role=normalized_actor_role,
                required_permission=required_permission,
                sensitive=sensitive,
                confirm_required=confirm_required,
                metadata=metadata,
            )
            self._record_decision(decision, parameters, user)
            return decision

        if sensitive and not confirm_supplied:
            reason = f"Tool '{tool_name}' is sensitive and requires confirm=True to execute."
            decision = SafetyDecision(
                allowed=False,
                reason=reason,
                tool_name=tool_name,
                actor_role=normalized_actor_role,
                required_permission=required_permission,
                sensitive=sensitive,
                confirm_required=confirm_required,
                metadata=metadata,
            )
            self._record_decision(decision, parameters, user)
            return decision

        actor_rank = _permission_rank(normalized_actor_role, self.permission_hierarchy)
        required_rank = _permission_rank(required_permission, self.permission_hierarchy)
        if actor_rank < required_rank:
            reason = (
                f"Tool '{tool_name}' requires permission '{required_permission}' "
                f"but actor role '{normalized_actor_role}' was provided."
            )
            decision = SafetyDecision(
                allowed=False,
                reason=reason,
                tool_name=tool_name,
                actor_role=normalized_actor_role,
                required_permission=required_permission,
                sensitive=sensitive,
                confirm_required=confirm_required,
                metadata=metadata,
            )
            self._record_decision(decision, parameters, user)
            return decision

        decision = SafetyDecision(
            allowed=True,
            reason=f"Tool '{tool_name}' authorized for execution.",
            tool_name=tool_name,
            actor_role=normalized_actor_role,
            required_permission=required_permission,
            sensitive=sensitive,
            confirm_required=confirm_required,
            metadata=metadata,
        )
        self._record_decision(decision, parameters, user)
        return decision

    def _record_decision(self, decision: SafetyDecision, parameters: Dict[str, Any], user: str) -> None:
        try:
            tool_audit.record_attempt(
                tool_name=decision.tool_name,
                parameters=parameters,
                allowed=decision.allowed,
                result=decision.reason if decision.allowed else None,
                error=None if decision.allowed else decision.reason,
                user=user,
                event="authorize",
                actor_role=decision.actor_role,
                sensitive=decision.sensitive,
                permission=decision.required_permission,
                reason=decision.reason,
            )
        except Exception:
            logger.exception("Failed to record safety decision for %s", decision.tool_name)
