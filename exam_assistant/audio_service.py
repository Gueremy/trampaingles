from __future__ import annotations

import os
import tempfile
import threading
import wave
from collections import deque
from collections.abc import Callable

import numpy as np
import soundcard as sc


class AudioTranscriptionService:
    def __init__(
        self,
        on_transcript: Callable[[str], None],
        notify: Callable[[str], None],
        chunk_seconds: int = 10,
        sample_rate: int = 16000,
    ):
        self.on_transcript = on_transcript
        self.notify = notify
        self.chunk_seconds = chunk_seconds
        self.sample_rate = sample_rate
        self.active = False
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._whisper_model = None
        self._whisper_lock = threading.Lock()
        self._recent_transcripts: deque[str] = deque(maxlen=6)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            self.notify("Audio capture is already active")
            return
        self.notify("Audio capture started")
        self.active = True
        self._stop.clear()
        self._thread = threading.Thread(target=self._audio_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self.active:
            return
        self.active = False
        self._stop.set()
        self.notify("Audio capture stopped")

    def _is_duplicate(self, transcript: str) -> bool:
        words = transcript.lower().split()
        recent = list(self._recent_transcripts)[-3:]
        for prev in recent:
            prev_words = prev.lower().split()
            if not prev_words:
                continue
            overlap = sum(1 for w in words[:12] if w in prev_words[-12:])
            threshold = min(6, max(3, int(len(words) * 0.65)))
            if overlap >= threshold:
                return True
        return False

    def _get_whisper_model(self):
        if self._whisper_model is None:
            with self._whisper_lock:
                if self._whisper_model is None:
                    from faster_whisper import WhisperModel

                    self._whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        return self._whisper_model

    def _find_loopback(self):
        for speaker in sc.all_speakers():
            try:
                return sc.get_microphone(speaker.id, include_loopback=True)
            except Exception:
                continue
        return None

    def _audio_loop(self) -> None:
        try:
            loopback = self._find_loopback()
            if loopback is None:
                self.notify("No loopback device was found")
                self.active = False
                return

            self.notify(f"Listening: {loopback.name[:30]}")
            with loopback.recorder(samplerate=self.sample_rate, channels=1) as recorder:
                while not self._stop.is_set():
                    data = recorder.record(numframes=self.sample_rate * self.chunk_seconds)
                    if self._stop.is_set():
                        break
                    rms = np.sqrt(np.mean(data**2))
                    if rms < 0.001:
                        continue
                    self._process_audio_chunk(data)
        except Exception as exc:
            self.notify(f"Audio error: {str(exc)[:80]}")
        finally:
            self.active = False

    def _process_audio_chunk(self, data) -> None:
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp.name
        tmp.close()
        try:
            with wave.open(tmp_path, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                pcm = (data * 32767).astype(np.int16)
                wav_file.writeframes(pcm.tobytes())
            self._transcribe_audio(tmp_path)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _transcribe_audio(self, wav_path: str) -> None:
        try:
            model = self._get_whisper_model()
            segments, _info = model.transcribe(wav_path, beam_size=1)
            transcript = " ".join(segment.text for segment in segments).strip()
            if transcript and len(transcript) > 10 and not self._is_duplicate(transcript):
                self._recent_transcripts.append(transcript)
                self.on_transcript(transcript)
                self.notify(f"Audio detected: {transcript[:40]}...")
        except Exception as exc:
            self.notify(f"Transcription failed: {str(exc)[:60]}")
