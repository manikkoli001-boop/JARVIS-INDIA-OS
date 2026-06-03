import importlib
import logging
import pkgutil
from typing import Any, Dict, Iterable, List, Optional

from core import tool_audit
from core.decorator import TOOL_REGISTRY
from core.safety_engine import SafetyEngine

logger = logging.getLogger(__name__)


class ToolNotFoundError(Exception):
    """Raised when a requested tool is not registered."""


class ToolManager:
    """Discover and execute registered tools from core package modules."""

    def __init__(self, package_name: str = "core", safety_engine: Optional[SafetyEngine] = None):
        self.package_name = package_name
        self.registry: Dict[str, Dict[str, Any]] = TOOL_REGISTRY
        self.safety_engine = safety_engine or SafetyEngine(registry=self.registry)
        self._discover_tools()

    def _discover_tools(self) -> None:
        """Import known package modules to populate TOOL_REGISTRY."""
        logger.debug("Discovering tools in package %s", self.package_name)
        try:
            package = importlib.import_module(self.package_name)
        except ModuleNotFoundError as exc:
            logger.error("Package %s not found: %s", self.package_name, exc)
            return

        if not hasattr(package, "__path__"):
            logger.warning("Package %s has no __path__ and cannot be discovered", self.package_name)
            return

        for module_info in self._iter_package_modules(package):
            full_name = f"{module_info.name}"
            try:
                if full_name == __name__:
                    continue
                logger.debug("Importing module %s for tool registration", full_name)
                importlib.import_module(full_name)
            except Exception as exc:
                logger.exception("Failed to import %s: %s", full_name, exc)

        logger.info("Tool discovery complete; %d tool(s) registered", len(self.registry))

    def _iter_package_modules(self, package: Any) -> Iterable[pkgutil.ModuleInfo]:
        """Walk the package and yield modules to import."""
        assert hasattr(package, "__path__")
        for module_info in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            if module_info.name.endswith(".test") or module_info.name.endswith(".tests"):
                continue
            if module_info.name.split(".")[-1].startswith("test_"):
                continue
            if module_info.ispkg:
                yield module_info
                subpackage = importlib.import_module(module_info.name)
                yield from self._iter_package_modules(subpackage)
            else:
                yield module_info

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Return tool metadata by name, or None if not found."""
        tool = self.registry.get(name)
        if tool is None:
            logger.warning("Requested tool '%s' is not registered", name)
        return tool

    def list_tools(self) -> List[str]:
        """Return the names of all registered tools."""
        return sorted(self.registry.keys())

    def execute_tool(self, name: str, *, actor_role: Optional[str] = None, user: str = "system", **kwargs: Any) -> Any:
        """Execute a registered tool by name using provided kwargs."""
        tool = self.get_tool(name)
        if tool is None:
            raise ToolNotFoundError(f"Tool '{name}' is not registered")

        func = tool.get("function")
        if not callable(func):
            logger.error("Tool '%s' does not contain a callable function", name)
            raise ToolNotFoundError(f"Tool '{name}' has no callable function")

        decision = self.safety_engine.authorize(
            tool_name=name,
            parameters=kwargs,
            actor_role=actor_role,
            user=user,
        )
        if not decision.allowed:
            logger.warning("Execution blocked for tool '%s': %s", name, decision.reason)
            return decision.reason

        try:
            logger.info("Executing tool '%s' with args %s", name, kwargs)
            result = func(**kwargs)
            try:
                tool_audit.record_attempt(
                    tool_name=name,
                    parameters=kwargs,
                    allowed=True,
                    result=result,
                    user=user,
                    event="execute",
                    actor_role=decision.actor_role,
                    sensitive=decision.sensitive,
                    permission=decision.required_permission,
                    reason=decision.reason,
                )
            except Exception:
                logger.debug("Failed to record audit for tool %s", name)
            return result
        except TypeError as exc:
            logger.exception("Argument mismatch when executing tool '%s'", name)
            try:
                tool_audit.record_attempt(
                    tool_name=name,
                    parameters=kwargs,
                    allowed=False,
                    error=str(exc),
                    user=user,
                    event="error",
                    actor_role=decision.actor_role,
                    sensitive=decision.sensitive,
                    permission=decision.required_permission,
                    reason=decision.reason,
                )
            except Exception:
                logger.debug("Failed to record audit error for tool %s", name)
            raise
        except Exception as exc:
            logger.exception("Error executing tool '%s'", name)
            try:
                tool_audit.record_attempt(
                    tool_name=name,
                    parameters=kwargs,
                    allowed=False,
                    error=str(exc),
                    user=user,
                    event="error",
                    actor_role=decision.actor_role,
                    sensitive=decision.sensitive,
                    permission=decision.required_permission,
                    reason=decision.reason,
                )
            except Exception:
                logger.debug("Failed to record audit error for tool %s", name)
            raise

    def get_tool_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve raw metadata for the named tool."""
        return self.get_tool(name)


def create_tool_manager() -> ToolManager:
    """Create a default ToolManager instance."""
    return ToolManager()
