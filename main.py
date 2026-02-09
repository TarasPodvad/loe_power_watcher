from datetime import datetime, timedelta
import hashlib
from scraper import fetch_group_lines
from alerts import parse_ranges, send_alerts
from plotter import generate_plot
from telegramer import send_telegram
from state import load_state, save_state
from alerts import parse_ranges, send_alerts_10min_window

print("RUN:", datetime.now().isoformat())

tracked_text = fetch_group_lines()

if not tracked_text:
    print("No data fetched")
    exit()

current_hash = hashlib.sha256(tracked_text.encode()).hexdigest()

lines = tracked_text.strip().splitlines()

today = datetime.now().date()
schedule_dates = [today + timedelta(days=i) for i in range(len(lines))]

# alerts
for line, sched_date in zip(lines, schedule_dates):
    send_alerts_10min_window(parse_ranges(line), sched_date)

# change detection
old_hash = load_state()

if old_hash != current_hash:
    dates = [(today + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(len(lines))]
    generate_plot(lines, dates)
    send_telegram(tracked_text, "data/schedule.png")
    save_state(current_hash)
else:
    print("no changes sent")