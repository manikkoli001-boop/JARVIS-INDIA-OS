import logging
import re
import sys
import time
from typing import Any, Dict, Optional

import pyttsx3
import speech_recognition as sr
from colorama import Fore, Style, init as colorama_init

from core.command_router import CommandRouter
from core.memory.memory_manager import memory_manager
from core.tool_manager import ToolManager

colorama_init(autoreset=True)
logger = logging.getLogger(__name__)


class VoiceAssistant:
    WAKE_WORD = "jarvis"
    EXIT_COMMANDS = {"exit", "quit", "stop", "shutdown", "bye"}
    HELP_COMMANDS = {"help", "commands", "what can you do"}
    TOOLS_COMMANDS = {"tools", "list tools", "show tools", "available tools"}
    MEMORY_COMMANDS = {"memory", "memories", "recent memory", "show memory", "recall memory"}

    def __init__(self, tool_manager: Optional[ToolManager] = None, router: Optional[CommandRouter] = None):
        self.tool_manager = tool_manager or ToolManager()
        self.router = router or CommandRouter(self.tool_manager)
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 160)
        self.engine.setProperty("volume", 1.0)
        self._welcome_message = "Jarvis voice assistant is active. Say the wake word Jarvis to begin."

    def _colored(self, text: str, color: str) -> str:
        return f"{color}{text}{Style.RESET_ALL}"

    def speak(self, text: str) -> None:
        if not text:
            return
        print(self._colored(f"Jarvis: {text}", Fore.CYAN))
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self, timeout: int = 5, phrase_time_limit: int = 7) -> str:
        with sr.Microphone() as source:
            print(self._colored("Listening...", Fore.YELLOW))
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = self.recognizer.recognize_google(audio)
                print(self._colored(f"You: {text}", Fore.GREEN))
                return text.strip()
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                self.speak("Sorry, I did not understand that. Please repeat.")
                return ""
            except sr.RequestError as exc:
                logger.error("Speech recognition request failed: %s", exc)
                self.speak("Speech recognition service is unavailable.")
                return ""
            except Exception as exc:
                logger.exception("Unexpected error during listening: %s", exc)
                self.speak("An error occurred while listening.")
                return ""

    def is_wake_word(self, text: str) -> bool:
        return bool(re.search(rf"\b{re.escape(self.WAKE_WORD)}\b", text, re.IGNORECASE))

    def extract_command(self, text: str) -> str:
        command = re.sub(rf"\b{re.escape(self.WAKE_WORD)}\b", "", text, flags=re.IGNORECASE).strip()
        return command

    def help_text(self) -> str:
        return (
            "I can execute tools and manage memory. "
            "Say 'Jarvis' first, then ask for: help, tools, memory, or a tool command like calculate or system info. "
            "You can also say exit to stop me."
        )

    def list_tools(self) -> str:
        tools = self.tool_manager.list_tools()
        return "Available tools: " + ", ".join(tools)

    def memory_summary(self) -> str:
        recent = memory_manager.list_recent_memories(limit=3)
        if not recent:
            return "No memories are stored yet."
        return "Recent memories: " + " | ".join(
            f"[{item['id']}] {item['category']}: {item['text']}" for item in recent
        )

    def handle_command(self, command: str) -> Dict[str, Any]:
        normalized = command.strip().lower()
        if not normalized:
            return {
                "tool": None,
                "intent": "none",
                "confidence": 0.0,
                "result": "I didn't catch that."
            }

        if normalized in self.EXIT_COMMANDS:
            return {"tool": "exit", "intent": "exit", "confidence": 1.0, "result": "shutdown"}
        if normalized in self.HELP_COMMANDS:
            return {"tool": "help", "intent": "help", "confidence": 1.0, "result": self.help_text()}
        if normalized in self.TOOLS_COMMANDS:
            return {"tool": "tools", "intent": "tools", "confidence": 1.0, "result": self.list_tools()}
        if normalized in self.MEMORY_COMMANDS:
            return {"tool": "memory", "intent": "memory", "confidence": 1.0, "result": self.memory_summary()}

        return self.router.route(command)

    def run(self) -> None:
        self.speak(self._welcome_message)
        while True:
            self.speak("Waiting for the wake word Jarvis.")
            phrase = self.listen(timeout=7, phrase_time_limit=5)
            if not phrase:
                continue

            if not self.is_wake_word(phrase):
                continue

            command = self.extract_command(phrase)
            if not command:
                self.speak("Yes? What can I do for you?")
                command = self.listen(timeout=7, phrase_time_limit=7)
                if not command:
                    continue

            if self.WAKE_WORD in command.lower():
                command = self.extract_command(command)

            response = self.handle_command(command)
            if response["tool"] == "exit":
                self.speak("Goodbye.")
                break

            if response["tool"] is None or response["intent"] == "unknown":
                fallback = "I could not find an action for that. Try asking for help or tools."
                self.speak(fallback)
            else:
                self.speak(str(response["result"]))
            time.sleep(0.5)


def main() -> None:
    assistant = VoiceAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
