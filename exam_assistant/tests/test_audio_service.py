import unittest
from unittest.mock import MagicMock, patch

from audio_service import AudioTranscriptionService


class AudioServiceTests(unittest.TestCase):
    def test_find_loopback_returns_first_supported_microphone(self):
        service = AudioTranscriptionService(lambda _text: None, lambda _msg: None)
        speaker_1 = MagicMock(id="a")
        speaker_2 = MagicMock(id="b")
        with patch("audio_service.sc.all_speakers", return_value=[speaker_1, speaker_2]), patch(
            "audio_service.sc.get_microphone", side_effect=[RuntimeError("x"), "mic-b"]
        ):
            self.assertEqual(service._find_loopback(), "mic-b")

    def test_process_audio_chunk_cleans_temp_file_and_transcribes(self):
        service = AudioTranscriptionService(lambda _text: None, lambda _msg: None)
        fake_data = MagicMock()
        fake_data.__mul__.return_value.astype.return_value.tobytes.return_value = b"pcm"
        with patch.object(service, "_transcribe_audio") as transcribe, patch("audio_service.os.unlink") as unlink:
            service._process_audio_chunk(fake_data)
            transcribe.assert_called_once()
            self.assertGreaterEqual(unlink.call_count, 1)

    def test_transcribe_audio_emits_transcript(self):
        seen = []
        service = AudioTranscriptionService(lambda text: seen.append(text), lambda _msg: None)
        seg1 = MagicMock(text="hello")
        seg2 = MagicMock(text=" world again")
        fake_model = MagicMock()
        fake_model.transcribe.return_value = ([seg1, seg2], MagicMock())
        with patch.object(service, "_get_whisper_model", return_value=fake_model):
            service._transcribe_audio("x.wav")
        self.assertEqual(seen, ["hello  world again"])


if __name__ == "__main__":
    unittest.main()
