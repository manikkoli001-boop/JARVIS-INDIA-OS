import unittest

from core.wakeword.wakeword_detector import WakeWordDetector


class WakeWordDetectorTest(unittest.TestCase):

    def setUp(self):
        self.detector = WakeWordDetector()

    def test_detects_wake_word(self):
        self.assertTrue(self.detector.detect("Hey Jarvis, open chrome"))

    def test_extracts_command(self):
        self.assertEqual(self.detector.extract_command("Jarvis open chrome"), "open chrome")

    def test_should_start_session(self):
        self.assertTrue(self.detector.should_start_session("Please Jarvis"))


if __name__ == "__main__":
    unittest.main()
