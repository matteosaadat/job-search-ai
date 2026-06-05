"""
Queue directory watcher — prints CHANGED to stdout whenever a file in the
watched directory is created or modified. Used with Claude Code's Monitor
tool so Claude is triggered instantly when the UI sends a chat message.

Usage:
    python watcher.py [queue_dir]

Default queue_dir: .jh/queue (relative to this file's location)
"""

import sys
import time
from pathlib import Path

def watch(queue_dir: Path, interval: float = 0.3):
    queue_dir.mkdir(parents=True, exist_ok=True)
    snapshot: dict[str, float] = {}

    def _scan() -> dict[str, float]:
        result = {}
        for f in queue_dir.glob("inbox-*.json"):
            try:
                result[f.name] = f.stat().st_mtime
            except OSError:
                pass
        return result

    snapshot = _scan()
    print(f"Watching {queue_dir}", flush=True)

    while True:
        time.sleep(interval)
        current = _scan()
        for name, mtime in current.items():
            if snapshot.get(name) != mtime:
                print("CHANGED", flush=True)
                break
        snapshot = current


if __name__ == "__main__":
    root = Path(__file__).parent
    queue_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else root / ".jh" / "queue"
    watch(queue_dir)
