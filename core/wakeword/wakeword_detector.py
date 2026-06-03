import re
from typing import Optional


class WakeWordDetector:
    def __init__(self, wake_word: str = "jarvis"):
        self.wake_word = wake_word.lower()
        self.pattern = re.compile(rf"\b{re.escape(self.wake_word)}\b", re.IGNORECASE)

    def detect(self, transcript: str) -> bool:
        if not transcript:
            return False
        return bool(self.pattern.search(transcript))

    def extract_command(self, transcript: str) -> str:
        if not transcript:
            return ""
        command = self.pattern.sub("", transcript)
        return command.strip()

    def normalize(self, transcript: str) -> str:
        return transcript.strip().lower() if transcript else ""

    def should_start_session(self, transcript: str) -> bool:
        return self.detect(transcript)
