import json
from datetime import date
from config import SENT_ALERTS_FILE

def _load() -> dict:
    if SENT_ALERTS_FILE.exists():
        try:
            return json.loads(SENT_ALERTS_FILE.read_text() or "{}")
        except json.JSONDecodeError:
            return {}
    return {}

def _save(data: dict) -> None:
    SENT_ALERTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def was_sent(event_id: str) -> bool:
    data = _load()
    return bool(data.get(event_id))

def mark_sent(event_id: str) -> None:
    data = _load()
    data[event_id] = True
    _save(data)

def prune_old(keep_from: date) -> None:
    """Optional: keep only current/future day entries."""
    data = _load()
    fresh = {k: v for k, v in data.items() if k[:10] >= keep_from.isoformat()}
    _save(fresh)
