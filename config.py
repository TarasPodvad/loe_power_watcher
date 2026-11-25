import os
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

API_URL = os.getenv(
    "API_URL",
    "https://api.loe.lviv.ua/api/menus?page=1&type=photo-grafic&jsonld=1",
)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = [c.strip() for c in os.getenv("CHAT_IDS", "").split(",") if c.strip()]
GROUP_NAME = os.getenv("GROUP_NAME", "Група 5.1.")
DRY_RUN = os.getenv("DRY_RUN") == "1"  # print instead of sending to Telegram

TZ = ZoneInfo("Europe/Kyiv")

BASE_DIR = Path(__file__).parent
# app folder is read-only in Azure -> use temp dir there (state itself lives in Blob)
DATA_DIR = Path(tempfile.gettempdir()) / "loe" if os.getenv("WEBSITE_INSTANCE_ID") else BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PLOT_FILE = DATA_DIR / "schedule.png"


def now() -> datetime:
    """Current Kyiv time as a naive datetime (schedule times are Kyiv-local)."""
    return datetime.now(TZ).replace(tzinfo=None)
