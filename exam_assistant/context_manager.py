from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from config import CONTEXT_FILE


class ContextManager:
    def __init__(self, context_file: Path = CONTEXT_FILE, max_entries: int = 20, max_chars: int = 8000):
        self.context_file = context_file
        self.max_entries = max_entries
        self.max_chars = max_chars
        self.entries: list[dict[str, str]] = []
        self.load()

    def load(self) -> None:
        if not self.context_file.exists():
            self.entries = []
            return
        try:
            loaded = json.loads(self.context_file.read_text(encoding="utf-8"))
            self.entries = loaded if isinstance(loaded, list) else []
        except (OSError, json.JSONDecodeError):
            self.entries = []

    def save(self) -> None:
        try:
            self.context_file.write_text(
                json.dumps(self.entries, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def add(self, role: str, content: str, source: str = "") -> None:
        entry = {
            "role": role,
            "content": content,
            "source": source,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        self.entries.append(entry)
        self._trim_entries()
        self.save()

    def _trim_entries(self) -> None:
        trimmed = self.entries[-self.max_entries :]
        total_chars = 0
        kept: list[dict[str, str]] = []
        for entry in reversed(trimmed):
            content_size = len(entry.get("content", ""))
            if kept and total_chars + content_size > self.max_chars:
                break
            kept.append(entry)
            total_chars += content_size
        self.entries = list(reversed(kept))

    def get_context_string(self) -> str:
        if not self.entries:
            return ""
        lines = ["=== MEMORIA RECIENTE DEL ASISTENTE ==="]
        for entry in self.entries:
            src = f" [{entry['source']}]" if entry.get("source") else ""
            lines.append(f"[{entry['time']}]{src} {entry['role'].upper()}: {entry['content'][:500]}")
        return "\n".join(lines)

    def get_structured_context(self, mode: str = "single") -> str:
        if not self.entries:
            return ""

        recent_audio = [entry for entry in self.entries if entry.get("role") == "audio"][-3:]
        recent_questions = [
            entry
            for entry in self.entries
            if entry.get("source") in {"full-screen", "screenshot", "manual-input", "text-selection"}
        ][-6:]
        recent_answers = [entry for entry in self.entries if entry.get("role") == "assistant"][-4:]

        lines = [f"=== STRUCTURED PRACTICE CONTEXT | MODE: {mode.upper()} ==="]
        if recent_audio:
            lines.append("[RECENT AUDIO]")
            for entry in recent_audio:
                lines.append(f"- {entry['time']}: {entry['content'][:280]}")
        if recent_questions:
            lines.append("[RECENT USER REQUESTS]")
            for entry in recent_questions:
                lines.append(f"- {entry['time']} {entry.get('source', '')}: {entry['content'][:280]}")
        if recent_answers:
            lines.append("[RECENT ANSWERS]")
            for entry in recent_answers:
                lines.append(f"- {entry['time']}: {entry['content'][:280]}")
        return "\n".join(lines)

    def get_practice_snapshot(self) -> dict:
        return {
            "audio": [entry for entry in self.entries if entry.get("role") == "audio"][-5:],
            "questions": [
                entry
                for entry in self.entries
                if entry.get("source") in {"full-screen", "screenshot", "manual-input", "text-selection"}
            ][-8:],
            "answers": [entry for entry in self.entries if entry.get("role") == "assistant"][-5:],
        }

    def clear(self) -> None:
        self.entries = []
        self.save()

    def count(self) -> int:
        return len(self.entries)
