import tempfile
import unittest
from pathlib import Path

from context_manager import ContextManager


class ContextManagerTests(unittest.TestCase):
    def test_trim_respects_entry_limit(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = ContextManager(context_file=Path(td) / "context.json", max_entries=3, max_chars=1000)
            for idx in range(5):
                ctx.add("user", f"msg-{idx}", "test")
            self.assertEqual(ctx.count(), 3)
            self.assertEqual(ctx.entries[0]["content"], "msg-2")

    def test_trim_respects_char_budget(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = ContextManager(context_file=Path(td) / "context.json", max_entries=10, max_chars=10)
            ctx.add("user", "12345", "a")
            ctx.add("assistant", "67890", "b")
            ctx.add("audio", "abcde", "c")
            self.assertEqual([entry["content"] for entry in ctx.entries], ["67890", "abcde"])

    def test_clear_persists_empty_state(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "context.json"
            ctx = ContextManager(context_file=path)
            ctx.add("user", "hola", "test")
            ctx.clear()
            self.assertEqual(ctx.count(), 0)
            self.assertIn("[]", path.read_text(encoding="utf-8"))

    def test_invalid_json_loads_empty_entries(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "context.json"
            path.write_text("{bad json", encoding="utf-8")
            ctx = ContextManager(context_file=path)
            self.assertEqual(ctx.entries, [])

    def test_large_entry_budget_keeps_most_recent_content(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = ContextManager(context_file=Path(td) / "context.json", max_entries=10, max_chars=20)
            ctx.add("user", "1111111111", "a")
            ctx.add("assistant", "2222222222", "b")
            ctx.add("audio", "3333333333", "c")
            self.assertEqual([entry["content"] for entry in ctx.entries], ["2222222222", "3333333333"])

    def test_structured_context_groups_recent_sections(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = ContextManager(context_file=Path(td) / "context.json")
            ctx.add("audio", "audio line", "system-audio")
            ctx.add("user", "screen request", "full-screen")
            ctx.add("assistant", "assistant answer", "ai")
            structured = ctx.get_structured_context("all")
            self.assertIn("STRUCTURED PRACTICE CONTEXT", structured)
            self.assertIn("[RECENT AUDIO]", structured)
            self.assertIn("[RECENT USER REQUESTS]", structured)
            self.assertIn("[RECENT ANSWERS]", structured)

    def test_practice_snapshot_groups_role_buckets(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = ContextManager(context_file=Path(td) / "context.json")
            ctx.add("audio", "audio line", "system-audio")
            ctx.add("user", "screen request", "manual-input")
            ctx.add("assistant", "assistant answer", "ai")
            snapshot = ctx.get_practice_snapshot()
            self.assertEqual(len(snapshot["audio"]), 1)
            self.assertEqual(len(snapshot["questions"]), 1)
            self.assertEqual(len(snapshot["answers"]), 1)


if __name__ == "__main__":
    unittest.main()
