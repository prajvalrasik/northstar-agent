"""Application configuration for Northstar Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent


@dataclass(slots=True)
class AppConfig:
    """Runtime configuration loaded from environment variables."""

    openai_api_key: str
    anthropic_api_key: str
    provider: str
    telegram_bot_token: str
    mode: str
    model_name: str
    host: str
    port: int
    storage_dir: Path
    memory_dir: Path
    approvals_file: Path
    pending_approvals_file: Path
    activity_log_file: Path
    sessions_db: Path
    workspace_dir: Path
    summary_threshold: int

    @property
    def enable_http(self) -> bool:
        return self.mode in {"http", "both"}

    @property
    def enable_telegram(self) -> bool:
        return self.mode in {"telegram", "both"}

    def ensure_directories(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def validate_for_runtime(self) -> None:
        if self.provider not in {"openai", "anthropic"}:
            raise ValueError("NORTHSTAR_PROVIDER must be one of: openai, anthropic.")
        if self.provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when NORTHSTAR_PROVIDER=openai.")
        if self.provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when NORTHSTAR_PROVIDER=anthropic.")
        if self.enable_telegram and not self.telegram_bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN is required when NORTHSTAR_MODE enables Telegram."
            )
        if self.mode not in {"http", "telegram", "both"}:
            raise ValueError("NORTHSTAR_MODE must be one of: http, telegram, both.")
        if self.summary_threshold < 4:
            raise ValueError("NORTHSTAR_SUMMARY_THRESHOLD must be at least 4.")


def _resolve_path(raw_value: str | None, default_relative: str) -> Path:
    if raw_value:
        candidate = Path(raw_value)
    else:
        candidate = ROOT_DIR / default_relative
    if not candidate.is_absolute():
        candidate = ROOT_DIR / candidate
    return candidate.resolve()


def load_config() -> AppConfig:
    """Load application configuration from the environment."""

    load_dotenv(dotenv_path=ROOT_DIR / ".env")

    storage_dir = _resolve_path(os.getenv("NORTHSTAR_STORAGE_DIR"), "storage")
    workspace_dir = _resolve_path(os.getenv("NORTHSTAR_WORKSPACE_DIR"), "workspace")

    provider = os.getenv("NORTHSTAR_PROVIDER", "openai").strip().lower() or "openai"
    default_model = "claude-sonnet-4-5" if provider == "anthropic" else "gpt-4o"

    return AppConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", "").strip(),
        provider=provider,
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        mode=os.getenv("NORTHSTAR_MODE", "both").strip().lower() or "both",
        model_name=os.getenv("NORTHSTAR_MODEL", default_model).strip() or default_model,
        host=os.getenv("NORTHSTAR_HOST", "0.0.0.0").strip() or "0.0.0.0",
        port=int(os.getenv("NORTHSTAR_PORT", "8080")),
        storage_dir=storage_dir,
        memory_dir=storage_dir / "memory",
        approvals_file=storage_dir / "exec-approvals.json",
        pending_approvals_file=storage_dir / "pending-approvals.json",
        activity_log_file=storage_dir / "activity.jsonl",
        sessions_db=storage_dir / "sessions.db",
        workspace_dir=workspace_dir,
        summary_threshold=int(os.getenv("NORTHSTAR_SUMMARY_THRESHOLD", "10")),
    )
