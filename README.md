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
TELEGRAM_CHAT_IDS=[id1,id2] #i.e. [123456789,234567890]

.env is intentionally not committed to GitHub.

---

## Run locally

python main.py

The script will:
- check current power status
- compare it with the previous state
- send a Telegram alert only if needed

## Run automatically on macOS (launchd)

This app can be run as a background service on macOS using **launchd**.
It will execute the script on a fixed interval and restart automatically.

### 1. Project location

Assume the project lives at:

/ABS/PATH/TO/loe-watcher-v2

Replace this path everywhere below with your actual absolute path.

---

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Create a launchd plist

Create the file:

~/Library/LaunchAgents/com.taras.loe-watcher-v2.plist

With the following content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.taras.loe-watcher-v2</string>

    <key>ProgramArguments</key>
    <array>
      <string>/ABS/PATH/TO/loe-watcher-v2/.venv/bin/python</string>
      <string>/ABS/PATH/TO/loe-watcher-v2/main.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/ABS/PATH/TO/loe-watcher-v2</string>

    <!-- Run every 60 seconds -->
    <key>StartInterval</key>
    <integer>60</integer>

    <!-- Run once immediately after load/login -->
    <key>RunAtLoad</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/ABS/PATH/TO/loe-watcher-v2/logs/loe-watcher.out.log</string>

    <key>StandardErrorPath</key>
    <string>/ABS/PATH/TO/loe-watcher-v2/logs/loe-watcher.err.log</string>

    <key>EnvironmentVariables</key>
    <dict>
      <key>PATH</key>
      <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
  </dict>
</plist>
```

Make sure the `logs/` directory exists:

```bash
mkdir -p logs
```

---

### 4. Load and start the service

```bash
launchctl load -w ~/Library/LaunchAgents/com.taras.loe-watcher-v2.plist
launchctl kickstart -k gui/$(id -u)/com.taras.loe-watcher-v2
```

---

### 5. Stop (unload) the service

```bash
launchctl unload -w ~/Library/LaunchAgents/com.taras.loe-watcher-v2.plist
```

---

### 6. Remove the service completely

```bash
launchctl unload -w ~/Library/LaunchAgents/com.taras.loe-watcher-v2.plist
rm ~/Library/LaunchAgents/com.taras.loe-watcher-v2.plist
```

---

### Notes

- The service runs under the **current user session**
- Logs are written to the `logs/` directory
- Configuration should be provided via environment variables (`.env`)
- After changing code or config, reload the service


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
