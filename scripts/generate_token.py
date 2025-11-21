#!/usr/bin/env python
"""
Generate a LiveKit access token for local development.

Usage:
    python scripts/generate_token.py
"""

from backend.config import load_config
from livekit import api


def main():
    cfg = load_config()

    token = (
        api.AccessToken(
            api_key=cfg.livekit.api_key,
            api_secret=cfg.livekit.api_secret,
        )
        .with_identity("local-web")
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

    print(token)


if __name__ == "__main__":
    main()

