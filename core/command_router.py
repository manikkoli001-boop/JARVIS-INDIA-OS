import inspect
import logging
from typing import Any, Dict, Optional

from core.intent_classifier import IntentClassifier, IntentResult
from core.tool_manager import ToolManager, ToolNotFoundError

logger = logging.getLogger(__name__)


class CommandRouter:
    """Route natural language commands to registered tools."""

    def __init__(self, tool_manager: Optional[ToolManager] = None, classifier: Optional[IntentClassifier] = None):
        self.tool_manager = tool_manager or ToolManager()
        self.classifier = classifier or IntentClassifier()

    def route(self, command: str) -> Dict[str, Any]:
        logger.info("Routing command: %s", command)
        intent = self.classifier.classify(command)
        if intent.tool_name is None:
            message = "Sorry, I could not determine an action from that command."
            logger.warning("Unknown intent for command '%s'", command)
            return {"command": command, "tool": None, "intent": "unknown", "confidence": 0.0, "result": message}

        tool = self.tool_manager.get_tool(intent.tool_name)
        if tool is None:
            message = f"The tool '{intent.tool_name}' is not available."
            logger.error(message)
            return {"command": command, "tool": intent.tool_name, "intent": intent.intent, "confidence": intent.confidence, "result": message}

        func = tool.get("function")
        if not callable(func):
            message = f"The tool '{intent.tool_name}' is not available."
            logger.error(message)
            return {"command": command, "tool": intent.tool_name, "intent": intent.intent, "confidence": intent.confidence, "result": message}

        try:
            signature = inspect.signature(func)
            signature.bind(**intent.parameters)
        except TypeError as exc:
            message = f"Tool '{intent.tool_name}' argument error: {exc}"
            logger.exception(message)
            return {"command": command, "tool": intent.tool_name, "intent": intent.intent, "confidence": intent.confidence, "result": message}

        try:
            response = self.tool_manager.execute_tool(intent.tool_name, **intent.parameters)
            logger.info("Command routed to tool %s with confidence %.2f", intent.tool_name, intent.confidence)
            return {
                "command": command,
                "tool": intent.tool_name,
                "intent": intent.intent,
                "confidence": round(intent.confidence, 2),
                "parameters": intent.parameters,
                "result": response,
            }
        except ToolNotFoundError:
            message = f"The tool '{intent.tool_name}' is not available."
            logger.error(message)
            return {"command": command, "tool": intent.tool_name, "intent": intent.intent, "confidence": intent.confidence, "result": message}
        except TypeError as exc:
            message = f"Tool '{intent.tool_name}' argument error: {exc}"
            logger.exception(message)
            return {"command": command, "tool": intent.tool_name, "intent": intent.intent, "confidence": intent.confidence, "result": message}
        except Exception as exc:
            message = f"An error occurred while executing '{intent.tool_name}': {exc}"
            logger.exception(message)
            return {"command": command, "tool": intent.tool_name, "intent": intent.intent, "confidence": intent.confidence, "result": message}
