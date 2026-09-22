"""
Unit tests for Voice management in UniversalSpeech.
"""
import unittest
from UniversalSpeech import UniversalSpeech, Voice, VoiceError


class TestVoices(unittest.TestCase):
    def setUp(self):
        self.speech = UniversalSpeech()

    def test_voice_dataclass(self):
        v = Voice(id=0, name="Test Voice")
        self.assertEqual(v.id, 0)
        self.assertEqual(v.name, "Test Voice")
        self.assertEqual(str(v), "Test Voice")
        self.assertIn("Voice(id=0, name='Test Voice')", repr(v))

    def test_get_voices(self):
        voices = self.speech.get_voices()
        self.assertIsInstance(voices, list)
        if self.speech.voice_supported:
            self.assertGreater(len(voices), 0)
            for v in voices:
                self.assertIsInstance(v, Voice)
                self.assertIsInstance(v.id, int)
                self.assertIsInstance(v.name, str)
                self.assertTrue(len(v.name) > 0)

    def test_get_voice_and_current_voice_property(self):
        if self.speech.voice_supported:
            voice = self.speech.get_voice()
            self.assertIsNotNone(voice)
            self.assertIsInstance(voice, Voice)
            self.assertEqual(self.speech.current_voice, voice)

    def test_set_voice_by_index(self):
        if self.speech.voice_supported:
            voices = self.speech.get_voices()
            if len(voices) > 0:
                self.speech.set_voice(0)
                current = self.speech.get_voice()
                self.assertEqual(current.id, 0)

    def test_set_voice_by_name(self):
        if self.speech.voice_supported:
            voices = self.speech.get_voices()
            if len(voices) > 0:
                target_name = voices[0].name
                self.speech.set_voice(target_name)
                current = self.speech.get_voice()
                self.assertEqual(current.name, target_name)

    def test_set_voice_by_object(self):
        if self.speech.voice_supported:
            voices = self.speech.get_voices()
            if len(voices) > 0:
                self.speech.set_voice(voices[0])
                current = self.speech.get_voice()
                self.assertEqual(current.id, voices[0].id)

    def test_set_voice_invalid_name_raises(self):
        if self.speech.voice_supported:
            with self.assertRaises(VoiceError):
                self.speech.set_voice("NonExistentVoiceXYZ_123456")

    def test_set_voice_invalid_type_raises(self):
        if self.speech.voice_supported:
            with self.assertRaises(TypeError):
                self.speech.set_voice([1, 2, 3])


if __name__ == "__main__":
    unittest.main()
