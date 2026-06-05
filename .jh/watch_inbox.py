"""
Background inbox watcher. Watches only the current session's inbox.
Exits with code 2 when an unclaimed message arrives.
"""
import json
import os
import time

QUEUE = os.path.join(os.path.dirname(__file__), "queue")
POLL_INTERVAL = 2
MAX_WAIT = 300  # 5 minutes


def current_inbox():
    session_file = os.path.join(QUEUE, "active-session.json")
    try:
        session = json.loads(open(session_file, encoding="utf-8").read())
        sid = session.get("session_id")
        if sid:
            return os.path.join(QUEUE, f"inbox-{sid}.json")
    except Exception:
        pass
    return None


def is_unclaimed(path):
    if not path or not os.path.exists(path):
        return False
    try:
        data = json.loads(open(path, encoding="utf-8").read())
        return data.get("claimed") is False and bool(data.get("id"))
    except Exception:
        return False


inbox = current_inbox()
if not inbox:
    exit(0)

deadline = time.time() + MAX_WAIT
while time.time() < deadline:
    time.sleep(POLL_INTERVAL)
    if is_unclaimed(inbox):
        exit(2)

exit(0)
