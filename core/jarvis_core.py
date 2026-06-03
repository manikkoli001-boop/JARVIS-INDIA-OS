import json
import logging
import re
from typing import Any, Dict, List, Optional

from core.agent import Agent
from core.conversation_history import ConversationHistory
from core.intent_classifier import IntentClassifier
from core.llm_client import OllamaClient
from core.memory.memory_manager import MemoryManager, memory_manager
from core.tool_manager import ToolManager, ToolNotFoundError

logger = logging.getLogger(__name__)


class JarvisAICore:
    """LLM-first Jarvis core orchestrator with tools, memory, and conversation history."""

    def __init__(
        self,
        tool_manager: Optional[ToolManager] = None,
        llm_client: Optional[OllamaClient] = None,
        memory: Optional[MemoryManager] = None,
        history: Optional[ConversationHistory] = None,
        classifier: Optional[IntentClassifier] = None,
        agent: Optional[Agent] = None,
    ):
        self.tool_manager = tool_manager or ToolManager()
        self.llm_client = llm_client or OllamaClient()
        self.memory = memory or memory_manager
        self.history = history or ConversationHistory()
        self.classifier = classifier or IntentClassifier()
        self.agent = agent or Agent(tool_manager=self.tool_manager, llm_client=self.llm_client, memory=self.memory, history=self.history)

    def process(self, user_input: str) -> Dict[str, Any]:
        user_input = user_input.strip()
        self.history.add_user_message(user_input)
        memory_context = self._build_memory_context(user_input)
        prompt_messages = self._build_prompt(user_input, memory_context)

        llm_output = self.llm_client.query(prompt_messages)
        parsed = self._parse_llm_response(llm_output)

        if parsed["tool"] is not None:
            reply = self._execute_tool(parsed["tool"], parsed["parameters"])
            tool = parsed["tool"]
            parameters = parsed["parameters"]
            agent_trace = []
        else:
            fallback = self._fallback_intent(user_input, parsed)
            if fallback["tool"] is not None:
                reply = self._execute_tool(fallback["tool"], fallback["parameters"])
                tool = fallback["tool"]
                parameters = fallback["parameters"]
                agent_trace = []
            else:
                agent_result = self.agent.run_task(user_input)
                reply = agent_result.get("result") if isinstance(agent_result, dict) else str(agent_result)
                plan = agent_result.get("plan") if isinstance(agent_result, dict) else None
                steps = plan.steps if hasattr(plan, "steps") else []
                tool = steps[-1].tool if steps else None
                parameters = steps[-1].parameters if steps else {}
                agent_trace = agent_result.get("trace") if isinstance(agent_result, dict) else []

        if self._should_save_memory(user_input):
            self._auto_save_memory(user_input)

        self.history.add_assistant_message(reply)
        return {
            "input": user_input,
            "tool": tool,
            "parameters": parameters,
            "result": reply,
            "agent_trace": agent_trace,
            "llm_output": llm_output,
            "memory_context": memory_context,
        }

    def _build_prompt(self, user_input: str, memory_context: str) -> List[Dict[str, str]]:
        tool_defs = self._format_tool_definitions()
        system_prompt = (
            "You are Jarvis, an AI assistant. Use available tools when they match the user's request. "
            "If a tool should be invoked, return only valid JSON with tool, parameters, and reply. "
            "If no tool is required, return JSON with tool set to null and include a natural language reply."
        )
        user_prompt = (
            f"Available tools:\n{tool_defs}\n\n"
            f"Memory context:\n{memory_context}\n\n"
            f"Conversation history:\n{self.history.as_prompt()}\n\n"
            f"User request:\n{user_input}\n\n"
            "Respond with a JSON object like: {'tool': 'tool_name' or null, 'parameters': {...}, 'reply': '...'}."
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _format_tool_definitions(self) -> str:
        entries = []
        for tool_name in self.tool_manager.list_tools():
            metadata = self.tool_manager.get_tool_metadata(tool_name) or {}
            description = metadata.get("description", "No description available.")
            entries.append(f"- {tool_name}: {description}")
        return "\n".join(entries) if entries else "(no tools available)"

    def _build_memory_context(self, user_input: str) -> str:
        recent_items = self.memory.list_recent_memories(limit=3)
        if not recent_items:
            return "No prior memories available."

        results = [f"- {item['text']} ({item['category']})" for item in recent_items]
        related_items = self.memory.search_memory(user_input)
        if related_items:
            results.append("\nRelated memories:")
            results.extend(f"- {item['text']} ({item['category']})" for item in related_items)
        return "\n".join(results)

    def _parse_llm_response(self, text: str) -> Dict[str, Any]:
        if not text:
            return {"tool": None, "parameters": {}, "reply": ""}

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except json.JSONDecodeError:
                    parsed = {"tool": None, "parameters": {}, "reply": text}
            else:
                parsed = {"tool": None, "parameters": {}, "reply": text}

        return {
            "tool": parsed.get("tool"),
            "parameters": parsed.get("parameters", {}),
            "reply": parsed.get("reply", ""),
        }

    def _fallback_intent(self, user_input: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        intent = self.classifier.classify(user_input)
        if intent.tool_name and intent.confidence >= 0.4:
            return {"tool": intent.tool_name, "parameters": intent.parameters, "reply": ""}
        return parsed

    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        try:
            result = self.tool_manager.execute_tool(tool_name, **parameters)
            logger.info("Executed tool %s successfully", tool_name)
            return str(result)
        except ToolNotFoundError:
            logger.warning("Tool %s not found during execution", tool_name)
            return f"I could not execute tool {tool_name}."
        except Exception as exc:
            logger.exception("Tool execution failed for %s: %s", tool_name, exc)
            return f"An error occurred while executing {tool_name}: {exc}"

    def _should_save_memory(self, text: str) -> bool:
        if not text or len(text) < 20:
            return False
        lower = text.lower().strip()
        if re.match(r"^(what|who|when|where|why|how|is|are|do|does|did|can|could|should|tell me|show|list)\b", lower):
            return False
        return True

    def _auto_save_memory(self, text: str) -> None:
        try:
            self.memory.save_memory(text=text, category="conversation")
        except Exception:
            logger.exception("Failed to auto-save memory for text: %s", text)
