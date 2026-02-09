from datetime import datetime, timedelta, date
from telegramer import send_telegram
from sent_alerts import was_sent, mark_sent

def _dt_from_minutes(d: date, minutes: int) -> datetime:
    return datetime.combine(d, datetime.min.time()) + timedelta(minutes=minutes)

def _fmt_hhmm(dt: datetime) -> str:
    return dt.strftime("%H:%M")

def send_alerts_10min_window(time_ranges, schedule_date: date):
    """
    Runs every ~10 minutes.
    Sends a single message if an event happens within the next 10 minutes.
    Message includes how long the upcoming state will last (until ...).
    """
    now = datetime.now()

    # Build concrete outage intervals (off_dt -> on_dt)
    intervals = []
    for start_min, end_min in time_ranges:
        crosses_midnight = end_min < start_min
        off_dt = _dt_from_minutes(schedule_date, start_min)
        on_dt = _dt_from_minutes(schedule_date + timedelta(days=1), end_min) if crosses_midnight else _dt_from_minutes(schedule_date, end_min)
        intervals.append((off_dt, on_dt))

    # Sort just in case
    intervals.sort(key=lambda x: x[0])

    for i, (off_dt, on_dt) in enumerate(intervals):
        # OFF event -> "no electricity in N minutes until HH:MM"
        _maybe_send_event(
            kind="OFF",
            event_dt=off_dt,
            until_dt=on_dt,
            now=now,
            template=lambda mins, until: f"⚠️ Світла не буде через {mins} хв. до {until}"
        )

        # ON event -> "electricity on in N minutes until next outage start (if exists)"
        next_off_dt = intervals[i + 1][0] if i + 1 < len(intervals) else None

        if next_off_dt:
            _maybe_send_event(
                kind="ON",
                event_dt=on_dt,
                until_dt=next_off_dt,
                now=now,
                template=lambda mins, until: f"✅ Світло буде через {mins} хв. до {until}"
            )
        else:
            # no next outage known -> message without "until"
            _maybe_send_event(
                kind="ON",
                event_dt=on_dt,
                until_dt=None,
                now=now,
                template=lambda mins, until: f"✅ Світло буде через {mins} хв."
            )

def _maybe_send_event(kind, event_dt, until_dt, now, template):
    diff_sec = (event_dt - now).total_seconds()
    if diff_sec <= 0:
        return

    # ceil minutes remaining
    diff_min = int((diff_sec + 59) // 60)

    if diff_min <= 10:
        event_id = f"{event_dt.date().isoformat()}_{kind}_{event_dt.strftime('%H:%M')}"
        if was_sent(event_id):
            return

        if until_dt is not None:
            msg = template(diff_min, until_dt.strftime("%H:%M"))
        else:
            msg = template(diff_min, None)

        send_telegram(msg)
        mark_sent(event_id)
