"""
Job Hunt queue watcher — prints CHANGED to stdout whenever any file in the queue directory changes.
Usage: python watcher.py <path-to-queue-directory>
"""
import sys
import time
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python watcher.py <queue-directory>", flush=True)
    sys.exit(1)

queue_dir = Path(sys.argv[1])
queue_dir.mkdir(parents=True, exist_ok=True)
print(f"Watching {queue_dir}", flush=True)


def _snapshot(d: Path) -> dict:
    snap = {}
    try:
        for f in d.iterdir():
            if f.is_file():
                snap[f.name] = f.stat().st_mtime
    except Exception:
        pass
    return snap


last = _snapshot(queue_dir)

while True:
    current = _snapshot(queue_dir)
    if current != last:
        last = current
        print("CHANGED", flush=True)
    time.sleep(0.3)
