import requests
from datetime import datetime
from config import BOT_TOKEN, CHAT_IDS

def send_telegram(msg=None, photo_path=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        if photo_path:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            for chat_id in CHAT_IDS:
                with open(photo_path, "rb") as img:
                    requests.post(
                        url,
                        data={"chat_id": chat_id, "caption": msg or ""},
                        files={"photo": img},
                        timeout=15
                    )
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            for chat_id in CHAT_IDS:
                requests.post(
                    url,
                    data={"chat_id": chat_id, "text": msg or ""},
                    timeout=15
                )
        print(now, msg)
    except requests.exceptions.RequestException as e:
        print(now, "Telegram error:", e)
