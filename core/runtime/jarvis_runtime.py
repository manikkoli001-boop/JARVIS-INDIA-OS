import logging
import re
import time
from typing import Optional

import pyttsx3
import speech_recognition as sr
from colorama import Fore, Style, init as colorama_init

from core.agent import Agent
from core.memory.memory_manager import memory_manager
from core.tool_manager import ToolManager
from core.wakeword.wakeword_detector import WakeWordDetector

colorama_init(autoreset=True)
logger = logging.getLogger(__name__)


class JarvisRuntime:
    WAKE_WORD = "jarvis"

    def __init__(self,
                 tool_manager: Optional[ToolManager] = None,
                 agent: Optional[Agent] = None,
                 wakeword_detector: Optional[WakeWordDetector] = None):
        self.tool_manager = tool_manager or ToolManager()
        self.agent = agent or Agent(tool_manager=self.tool_manager)
        self.wakeword_detector = wakeword_detector or WakeWordDetector(self.WAKE_WORD)
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 160)
        self.engine.setProperty("volume", 1.0)
        self._running = False

    def _colored(self, text: str, color: str) -> str:
        return f"{color}{text}{Style.RESET_ALL}"

    def speak(self, text: str) -> None:
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
                self.speak("Speech recognition is unavailable.")
                return ""
            except Exception as exc:
                logger.exception("Voice listen error: %s", exc)
                self.speak("An unexpected error occurred while listening.")
                return ""

    def run(self) -> None:
        self._running = True
        self.speak("Jarvis is ready. Say the wake word to begin.")
        while self._running:
            transcript = self.listen(timeout=7, phrase_time_limit=5)
            if not transcript:
                continue
            if not self.wakeword_detector.should_start_session(transcript):
                continue
            command = self.wakeword_detector.extract_command(transcript)
            if not command:
                self.speak("Yes? What do you want me to do?")
                command = self.listen(timeout=7, phrase_time_limit=7)
            if not command:
                continue
            response = self._process_command(command)
            self.speak(response)
            time.sleep(0.5)

    def _process_command(self, command: str) -> str:
        if command.strip().lower() in {"exit", "quit", "stop", "shutdown", "bye"}:
            self._running = False
            return "Goodbye."

        result = self.agent.run_task(command)
        if isinstance(result, dict):
            return result.get("result", "I completed the task.")
        return str(result)

    def stop(self) -> None:
        self._running = False


def main() -> None:
    runtime = JarvisRuntime()
    runtime.run()


if __name__ == "__main__":
    main()
