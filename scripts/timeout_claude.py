#!/usr/bin/env python3
"""Run a command with a hard timeout, killing the entire process group on expiry.

Usage:
    timeout_claude.py <seconds> <command> [args...]

Exit code:
    - whatever the child exits with on success
    - 124 if killed by the timeout (mirrors GNU `timeout` behaviour)

Why this exists: macOS lacks `gtimeout` by default, and `claude` (Node-based)
spawns child processes that escape a naive SIGKILL of just the parent. We
start the child in its own session and SIGKILL the whole group on timeout.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: timeout_claude.py <seconds> <cmd> [args...]", file=sys.stderr)
        return 2
    try:
        timeout = float(sys.argv[1])
    except ValueError:
        print(f"bad timeout: {sys.argv[1]!r}", file=sys.stderr)
        return 2
    cmd = sys.argv[2:]

    proc = subprocess.Popen(
        cmd,
        stdout=None,  # inherit, so the wrapper is transparent
        stderr=None,
        stdin=None,
        start_new_session=True,
    )

    killed = {"by_watchdog": False}

    def _on_deadline() -> None:
        killed["by_watchdog"] = True
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, OSError):
            pass

    timer = threading.Timer(timeout, _on_deadline)
    timer.start()
    try:
        rc = proc.wait()
    finally:
        timer.cancel()

    if killed["by_watchdog"]:
        return 124
    return rc


if __name__ == "__main__":
    sys.exit(main())
