#!/usr/bin/env python
"""
Generate a LiveKit access token for local development.

Usage:
    source .venv/bin/activate
    python scripts/generate_token.py

This prints a JWT you can paste into `frontend/.env.local` as VITE_LIVEKIT_TOKEN.
"""

from __future__ import annotations

from backend.config import load_config
from livekit import api


def generate_token(identity: str = "local-web") -> str:
    """
    Generate a JWT with permissions to join the default LiveKit room.

    - identity: human-readable identity for the browser client.
    """
    cfg = load_config()

    token = (
        api.AccessToken(
            api_key=cfg.livekit.api_key,
            api_secret=cfg.livekit.api_secret,
        )
        .with_identity(identity)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=cfg.livekit.default_room,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .to_jwt()
    )
    return token


def main() -> None:
    print(generate_token())


if __name__ == "__main__":
    main()