import unittest
from types import SimpleNamespace

from ai_client import AIClient, is_error_response


class DummyCompletions:
    def __init__(self, content="ok", exc=None):
        self.content = content
        self.exc = exc
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.exc:
            raise self.exc
        message = SimpleNamespace(content=self.content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class DummyOpenAI:
    def __init__(self, content="ok", exc=None):
        self.completions = DummyCompletions(content=content, exc=exc)
        self.chat = SimpleNamespace(completions=self.completions)


class AIClientTests(unittest.TestCase):
    def test_ask_text_uses_reasoning_extra_body_for_reasoning_models(self):
        backend = DummyOpenAI()
        client = AIClient(
            api_key="test",
            model="demo-reasoning",
            user_rules_loader=lambda: "breve",
            openai_factory=lambda **_: backend,
        )
        reply = client.ask_text("hola", "ctx")
        self.assertEqual(reply, "ok")
        self.assertIn("extra_body", backend.completions.calls[0])

    def test_ask_image_sends_data_url(self):
        backend = DummyOpenAI()
        client = AIClient(
            api_key="test",
            user_rules_loader=lambda: "",
            openai_factory=lambda **_: backend,
        )
        client.ask_image(b"img", "ctx")
        payload = backend.completions.calls[0]["messages"][0]["content"][1]["image_url"]["url"]
        self.assertTrue(payload.startswith("data:image/png;base64,"))

    def test_error_response_is_flagged(self):
        backend = DummyOpenAI(exc=RuntimeError("boom"))
        client = AIClient(
            api_key="test",
            user_rules_loader=lambda: "",
            openai_factory=lambda **_: backend,
        )
        reply = client.ask_text("hola", "")
        self.assertTrue(is_error_response(reply))

    def test_non_reasoning_model_skips_extra_body(self):
        backend = DummyOpenAI()
        client = AIClient(
            api_key="test",
            model="demo-standard",
            user_rules_loader=lambda: "",
            openai_factory=lambda **_: backend,
        )
        client.ask_text("hola", "ctx")
        self.assertNotIn("extra_body", backend.completions.calls[0])

    def test_prompt_includes_user_rules_and_context(self):
        backend = DummyOpenAI()
        client = AIClient(
            api_key="test",
            model="demo-standard",
            user_rules_loader=lambda: "short answers",
            openai_factory=lambda **_: backend,
        )
        client.ask_text("question", "ctx-data")
        prompt = backend.completions.calls[0]["messages"][0]["content"]
        self.assertIn("short answers", prompt)
        self.assertIn("ctx-data", prompt)

    def test_parse_extracted_questions_returns_normalized_list(self):
        client = AIClient(
            api_key="test",
            user_rules_loader=lambda: "",
            openai_factory=lambda **_: DummyOpenAI(),
        )
        raw = '{"questions":[{"id":1,"prompt":"What is 2+2?","choices":["A","B"],"notes":"visible"}]}'
        parsed = client._parse_extracted_questions(raw)
        self.assertEqual(parsed[0]["id"], "1")
        self.assertEqual(parsed[0]["prompt"], "What is 2+2?")
        self.assertEqual(parsed[0]["choices"], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
