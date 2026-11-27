import re
from datetime import datetime, timedelta

from config import now as kyiv_now

ALERT_WINDOW_MIN = 10


def _to_minutes(t: str) -> int:
    h, m = map(int, t.split(":"))
    return h * 60 + m  # "24:00" -> 1440


def parse_ranges(line: str):
    matches = re.findall(r"з\s*(\d{1,2}:\d{2})\s*до\s*(\d{1,2}:\d{2})", line or "", flags=re.IGNORECASE)
    return [(_to_minutes(s), _to_minutes(e)) for s, e in matches]


def _intervals(schedule):
    """All outage intervals across all dates, as datetimes, with touching ones merged."""
    out = []
    for d, line in schedule:
        base = datetime.combine(d, datetime.min.time())
        for start, end in parse_ranges(line):
            off = base + timedelta(minutes=start)
            on = base + timedelta(minutes=end if end >= start else end + 24 * 60)
            out.append([off, on])
    out.sort()
    merged = []
    for off, on in out:
        if merged and off <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], on)
        else:
            merged.append([off, on])
    return merged


def plan_alerts(schedule, lead_min: int = ALERT_WINDOW_MIN):
    """For queue-based delivery: [(send_at, event_id, text)] for every future event.

    send_at = event - lead_min; if that moment already passed but the event is still
    ahead, send_at = now and the text uses the real minutes left.
    """
    now = kyiv_now()
    intervals = _intervals(schedule)
    plan = []
    for i, (off_dt, on_dt) in enumerate(intervals):
        nxt = intervals[i + 1][0] if i + 1 < len(intervals) else None
        events = [
            ("OFF", off_dt, "⚠️ Світла не буде через {mins} хв. до " + f"{on_dt:%H:%M}"),
            ("ON", on_dt, "✅ Світло буде через {mins} хв." + (f" до {nxt:%H:%M}" if nxt else "")),
        ]
        for kind, event_dt, tmpl in events:
            if event_dt <= now:
                continue
            send_at = max(event_dt - timedelta(minutes=lead_min), now)
            mins = int(((event_dt - send_at).total_seconds() + 59) // 60)
            plan.append((send_at, f"{event_dt:%Y-%m-%d}_{kind}_{event_dt:%H:%M}", tmpl.format(mins=mins)))
    return plan


def describe_change(old_text: str, new_text: str) -> str:
    """Human-readable diff of the group's lines, keyed by date. Past dates are ignored,
    so yesterday dropping off the site at midnight is not reported as a change."""
    today = kyiv_now().date()

    def by_date(t):
        rows = dict(l.split(": ", 1) for l in (t or "").splitlines() if ": " in l)
        return {d: v for d, v in rows.items() if datetime.strptime(d, "%d.%m.%Y").date() >= today}

    old, new = by_date(old_text), by_date(new_text)
    out = []
    for d in sorted(set(old) | set(new), key=lambda s: s[6:] + s[3:5] + s[:2]):
        o, n = old.get(d), new.get(d)
        if o == n:
            continue
        short = lambda s: s.split(". ", 1)[-1] if s else "—"
        if o is None:
            out.append(f"🆕 {d}: {short(n)}")
        elif n is None:
            out.append(f"🗑 {d}: графік знято")
        else:
            out.append(f"🔄 {d}: {short(o)} → {short(n)}")
    return "\n".join(out)


WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]


def _hm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def format_caption(old_text: str, new_text: str) -> str:
    """Short, preview-friendly caption: one line per upcoming day, times first.

    e.g. '🔴 Пт 27.11: 10:00–13:30, 20:00–23:30 · змінено'
    """
    today = kyiv_now().date()

    def by_date(t):
        rows = dict(l.split(": ", 1) for l in (t or "").splitlines() if ": " in l)
        return {datetime.strptime(d, "%d.%m.%Y").date(): v for d, v in rows.items()
                if datetime.strptime(d, "%d.%m.%Y").date() >= today}

    old, new = by_date(old_text), by_date(new_text)
    lines = []
    for d in sorted(set(old) | set(new)):
        label = f"{WEEKDAYS[d.weekday()]} {d:%d.%m}"
        if d not in new:
            lines.append(f"⚪️ {label}: графік знято")
            continue
        ranges = parse_ranges(new[d])
        body = ", ".join(f"{_hm(a)}–{_hm(b)}" for a, b in ranges) if ranges else "світло весь день"
        mark = "" if old.get(d) == new[d] else (" · новий" if d not in old else " · змінено")
        lines.append(f"{'🔴' if ranges else '🟢'} {label}: {body}{mark}")
    return "\n".join(lines)
