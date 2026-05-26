from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

CONFIG_FILE = APP_DIR / "config.env"
RULES_FILE = APP_DIR / "instrucciones.txt"
CONTEXT_FILE = APP_DIR / "context.json"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openrouter/free"


def load_config(config_file: Path = CONFIG_FILE) -> dict[str, str]:
    cfg: dict[str, str] = {}
    if not config_file.exists():
        return cfg

    for raw_line in config_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or "=" not in line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        cfg[key.strip()] = value.strip()
    return cfg


def load_user_rules(rules_file: Path = RULES_FILE) -> str:
    if not rules_file.exists():
        return ""
    try:
        return rules_file.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


@dataclass(slots=True)
class AppConfig:
    api_key: str
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    monitor_index: int = 1

    @classmethod
    def from_file(cls, config_file: Path = CONFIG_FILE) -> "AppConfig":
        raw = load_config(config_file)
        return cls(
            api_key=raw.get("OPENROUTER_API_KEY", ""),
            model=raw.get("AI_MODEL", DEFAULT_MODEL),
            base_url=raw.get("AI_BASE_URL", DEFAULT_BASE_URL),
            monitor_index=int(raw.get("MONITOR_INDEX", "1")),
        )
