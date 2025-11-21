"""
Configuration helpers for the Skyline Motors voice concierge backend.

This keeps all environment variable access in one place so the rest of the
code can depend on a simple, typed config object.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import os


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"


def _load_env() -> None:
    """
    Load environment variables from a local `.env` file if present.

    This is convenient for local development; on real deployments you can
    rely on the process environment instead.
    """

    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)


@dataclass
class LiveKitConfig:
    url: str
    api_key: str
    api_secret: str
    default_room: str


@dataclass
class OpenAIConfig:
    api_key: str
    # Model names are kept as plain strings so they are trivial to tweak.
    fast_model: str = "gpt-4o-mini"
    slow_model: str = "gpt-4o-mini"
    stt_model: str = "gpt-4o-mini-transcribe"
    tts_model: str = "gpt-4o-mini-tts"


@dataclass
class RagConfig:
    dealer_handbook_path: Path
    top_k_chunks: int = 3


@dataclass
class AppConfig:
    livekit: LiveKitConfig
    openai: OpenAIConfig
    rag: RagConfig


def load_config() -> AppConfig:
    """Load configuration from environment variables and `.env`."""
    _load_env()

    livekit_url = os.getenv("LIVEKIT_URL", "").strip()
    livekit_api_key = os.getenv("LIVEKIT_API_KEY", "").strip()
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", "").strip()
    room_name = os.getenv("LIVEKIT_ROOM_NAME", "skyline-showroom").strip()

    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not livekit_url or not livekit_api_key or not livekit_api_secret:
        raise RuntimeError(
            "LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET must be set "
            "in the environment or .env file."
        )

    if not openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY must be set in the environment or .env file."
        )

    handbook_path_env: Optional[str] = os.getenv("DEALER_HANDBOOK_PATH")
    if handbook_path_env:
        handbook_path = Path(handbook_path_env).expanduser()
    else:
        handbook_path = PROJECT_ROOT / "backend" / "resources" / "dealer_handbook.pdf"

    return AppConfig(
        livekit=LiveKitConfig(
            url=livekit_url,
            api_key=livekit_api_key,
            api_secret=livekit_api_secret,
            default_room=room_name,
        ),
        openai=OpenAIConfig(api_key=openai_api_key),
        rag=RagConfig(dealer_handbook_path=handbook_path),
    )


__all__ = ["AppConfig", "LiveKitConfig", "OpenAIConfig", "RagConfig", "load_config"]


