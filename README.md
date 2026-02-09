# LOE Power Watcher ⚡

A small Python service that monitors power availability on  
https://poweron.loe.lviv.ua and sends Telegram alerts when the power
goes off or comes back.

Designed to run continuously (locally, cron, or cloud) and notify only
when something actually changes.

---

## What it does

- Scrapes power status from the LOE website
- Detects power off / power on transitions
- Sends Telegram notifications
- Avoids duplicate alerts using local state
- Can generate simple plots of power history

---

## Project structure

.
├── main.py            # Entry point
├── scraper.py         # Fetches & parses power status
├── alerts.py          # Alert decision logic
├── telegramer.py      # Telegram message sender
├── state.py           # Runtime state handling
├── sent_alerts.py     # Prevents duplicate notifications
├── plotter.py         # Power history plotting
├── config.py          # App configuration
├── requirements.txt   # Python dependencies

---

## Requirements

- Python 3.10+
- pip

Install dependencies:

pip install -r requirements.txt

---

## Configuration

Create a .env file in the project root:

TELEGRAM_BOT_TOKEN=your_bot_token  
TELEGRAM_CHAT_IDS=123456789,987654321

.env is intentionally not committed to GitHub.

---

## Run locally

python main.py

The script will:
- check current power status
- compare it with the previous state
- send a Telegram alert only if needed

---

## State & persistence

The app uses local files to remember previous status and sent alerts:

- state.txt
- sent_alerts.json

These files are:
- created automatically
- ignored by Git (.gitignore)
- safe to delete if you want a fresh start

---

## Deployment notes

This project can be run as:
- a local background script
- a cron job
- an Azure Function or container (with small adjustments)

Secrets should always be injected via environment variables.

---

## Disclaimer

This project depends on the public LOE website structure.
If the site changes, scraping logic may need updates.

---

## License

Personal use.
