#!/usr/bin/env python
"""
Small developer helper to run the LiveKit agent worker and the upload helper
server in a single terminal.

Usage (from project root, with virtualenv activated):

    python scripts/run_backend.py

This will:
- start `python -m backend.agent start`
- start `python -m backend.upload_server`

Press Ctrl+C to stop both.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import List


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    commands = [
        [sys.executable, "-m", "backend.agent", "start"],
        [sys.executable, "-m", "backend.upload_server"],
    ]

    procs: List[subprocess.Popen[bytes]] = []

    try:
        for cmd in commands:
            proc = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT),
            )
            procs.append(proc)

        print("Started backend agent and helper server.")
        print("Logs from both processes will appear in this terminal.")
        print("Press Ctrl+C to stop them.")

        # Keep the parent process alive until one child exits or user interrupts.
        while True:
            time.sleep(1.0)
            for proc in procs:
                code = proc.poll()
                if code is not None:
                    raise SystemExit(
                        f"Subprocess {proc.args} exited with code {code}. "
                        "Stopping remaining processes."
                    )
    except KeyboardInterrupt:
        print("\nStopping backend processes...")
    finally:
        for proc in procs:
            if proc.poll() is None:
                proc.terminate()

        # Give them a moment to exit cleanly before forcing.
        for proc in procs:
            try:
                proc.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    main()


