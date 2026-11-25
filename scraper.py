import html
import re
import time
from datetime import date, datetime

import requests

from config import API_URL, GROUP_NAME

DATE_RE = re.compile(r"на\s+(\d{2}\.\d{2}\.\d{4})")


def _text_lines(raw_html: str):
    text = html.unescape(re.sub(r"<[^>]+>", "\n", raw_html or ""))
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def fetch_schedule() -> list[tuple[date, str]]:
    """Return [(schedule_date, group_line), ...] for GROUP_NAME only.

    Empty list = no schedule published for the group (a normal state, not an error).
    Raises on network/format errors so the run fails loudly.
    """
    # API sends cache-control max-age=3600 / s-maxage=7200 -> bypass CDN/proxy caches
    resp = requests.get(
        API_URL,
        params={"_": int(time.time())},
        timeout=20,
        headers={"User-Agent": "loe-power-watcher", "Cache-Control": "no-cache"},
    )
    resp.raise_for_status()
    items = resp.json()["hydra:member"][0]["menuItems"]

    result = []
    for item in sorted(items, key=lambda i: i.get("orders", 0)):
        current_date = None
        for line in _text_lines(item.get("rawHtml")):
            m = DATE_RE.search(line)
            if m and line.startswith("Графік"):
                current_date = datetime.strptime(m.group(1), "%d.%m.%Y").date()
            elif line.startswith(GROUP_NAME) and current_date:
                result.append((current_date, line))
    # de-dup (same date may appear in several items) and sort by date
    return sorted(dict.fromkeys(result))
