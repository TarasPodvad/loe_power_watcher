# LOE Power Watcher ⚡

A small Python service that monitors power availability on  
https://poweron.loe.lviv.ua and sends Telegram alerts when the power
goes off or comes back.

Runs in Azure Functions and notifies only when your group's schedule changes.

---

## What it does

- Reads the schedule from the LOE JSON API (`api.loe.lviv.ua`, the same source the website uses; no browser)
- Tracks **only your group** (`GROUP_NAME`), ignores changes in other groups
- On a change, sends a chart + a readable diff, e.g. `🔄 25.11.2026: Електроенергія є. → Електроенергії немає з 13:00 до 16:30.`
- Sends "⚠️ Світла не буде через 10 хв." / "✅ Світло буде через 10 хв." at the exact time
  (alerts are queued with a delay; if the schedule changes, old alerts are dropped)

## How it runs (Azure Functions, Flex Consumption)

| Function | Trigger | Does |
|---|---|---|
| `check_schedule` | timer, every 5 min | fetch API → diff vs last state (Blob) → notify → queue alerts |
| `send_alert` | Storage Queue `loe-alerts` | fires at alert time, skips if schedule changed since |

State lives in Blob container `loe-state` (`schedule.txt`, `version.txt`).

---

## Project structure

.
├── function_app.py    # Azure Functions entry (timer + queue)
├── watcher.py         # Core: fetch → diff → notify → plan alerts
├── scraper.py         # LOE API client, keeps only GROUP_NAME lines
├── alerts.py          # Parse ranges, plan alerts, describe changes
├── telegramer.py      # Telegram sender (DRY_RUN supported)
├── plotter.py         # Schedule chart
├── storage.py         # State in Azure Blob
├── config.py          # Settings, Kyiv time
├── deploy.sh          # One-time Azure setup + deploy

---

## Requirements

- Azure subscription
- Azure CLI (`az`)

## Configuration

Function App settings (set by `deploy.sh`, never committed):

| Setting | Example |
|---|---|
| `BOT_TOKEN` | Telegram bot token |
| `CHAT_IDS` | `123456789,234567890` — every chat gets every message |
| `GROUP_NAME` | `Група 5.1.` |
| `DRY_RUN` | `1` = log messages instead of sending (optional) |

Times are always Europe/Kyiv.

## Deploy

```bash
az login
export BOT_TOKEN=... CHAT_IDS=123,456
az account set --subscription "<name or id>"
./deploy.sh    # creates what's missing, updates settings, deploys committed code; re-run for updates
```

---

## Costs, stop, delete

- **Cost:** ~€0/month. ~8,700 runs/month fits the Flex Consumption free grant
  (250,000 executions + 100,000 GB-s per subscription); storage and App Insights are cents.
- **Pause:** portal → Function App `loe-watcher-taras` → Overview → **Stop** (Start to resume).
- **Delete:** portal → resource group `rg-loe-watcher` → **Delete resource group**
  (or `az group delete -n rg-loe-watcher`). Also check `DefaultResourceGroup-*` for an
  auto-created Log Analytics workspace and delete it if nothing else uses it.

---

## Disclaimer

This project depends on the public LOE API (`api.loe.lviv.ua`).
If its format changes, `scraper.py` may need updates.

---

## License

Personal use.
