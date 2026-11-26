"""Core logic, shared by the Azure Function and the local runner."""
import hashlib

from alerts import describe_change, plan_alerts
from config import GROUP_NAME, PLOT_FILE
from plotter import generate_plot
from scraper import fetch_schedule
from storage import get_text, put_text
from telegramer import send_telegram


def check(enqueue) -> str:
    """Fetch schedule; on a real change for the group: notify + plan alerts.

    enqueue(send_at, version, event_id, text) schedules one alert message.
    """
    schedule = fetch_schedule()
    new_text = "\n".join(f"{d:%d.%m.%Y}: {line}" for d, line in schedule)
    old_text = get_text("schedule.txt")
    if old_text == new_text:
        return "no changes"

    put_text("schedule.txt", new_text)
    diff = describe_change(old_text, new_text)
    if not diff:  # only a past day dropped off at midnight
        return "rollover, nothing new"

    # new version -> alerts queued for older versions get ignored
    version = hashlib.sha256(new_text.encode()).hexdigest()[:12]
    put_text("version.txt", version)

    caption = f"{GROUP_NAME.rstrip('.')} — зміни в графіку:\n{diff}"
    if schedule:
        generate_plot(schedule)
        send_telegram(caption, PLOT_FILE)
    else:
        send_telegram(caption)

    plan = plan_alerts(schedule)
    for send_at, event_id, text in plan:
        enqueue(send_at, version, event_id, text)
    return f"changed, {len(plan)} alerts planned"
