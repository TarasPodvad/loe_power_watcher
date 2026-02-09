from dotenv import load_dotenv
import os
from pathlib import Path
import json
from pathlib import Path

load_dotenv()

URL = os.getenv("URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS").split(",")
GROUP_NAME = os.getenv("GROUP_NAME")

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "data" / "state.txt"
PLOT_FILE = BASE_DIR / "data" / "schedule.png"

SENT_ALERTS_FILE = BASE_DIR / "data" / "sent_alerts.json"
