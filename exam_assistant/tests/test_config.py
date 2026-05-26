import tempfile
import unittest
from pathlib import Path

from config import AppConfig, load_config, load_user_rules


class ConfigTests(unittest.TestCase):
    def test_load_config_parses_key_values(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "config.env"
            path.write_text("# comment\nOPENROUTER_API_KEY=test\nAI_MODEL=model-x\n", encoding="utf-8")
            cfg = load_config(path)
            self.assertEqual(cfg["OPENROUTER_API_KEY"], "test")
            self.assertEqual(cfg["AI_MODEL"], "model-x")

    def test_load_user_rules_returns_empty_when_missing(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "instrucciones.txt"
            self.assertEqual(load_user_rules(path), "")

    def test_app_config_uses_defaults(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "config.env"
            path.write_text("OPENROUTER_API_KEY=test\n", encoding="utf-8")
            cfg = AppConfig.from_file(path)
            self.assertEqual(cfg.api_key, "test")
            self.assertTrue(cfg.model)
            self.assertTrue(cfg.base_url)


if __name__ == "__main__":
    unittest.main()
