import requests

from config import BOT_TOKEN, CHAT_IDS, DRY_RUN, now

API = "https://api.telegram.org/bot{token}/{method}"


def send_telegram(msg=None, photo_path=None):
    stamp = now().strftime("%Y-%m-%d %H:%M:%S")
    if DRY_RUN:
        print(f"{stamp} [DRY RUN] would send{' photo' if photo_path else ''}:", msg)
        return

    for chat_id in CHAT_IDS:
        try:
            if photo_path:
                with open(photo_path, "rb") as img:
                    r = requests.post(
                        API.format(token=BOT_TOKEN, method="sendPhoto"),
                        data={"chat_id": chat_id, "caption": msg or ""},
                        files={"photo": img},
                        timeout=15,
                    )
            else:
                r = requests.post(
                    API.format(token=BOT_TOKEN, method="sendMessage"),
                    data={"chat_id": chat_id, "text": msg or ""},
                    timeout=15,
                )
            if not r.ok:
                print(stamp, f"Telegram error for {chat_id}: {r.status_code} {r.text[:200]}")
        except requests.exceptions.RequestException as e:
            print(stamp, f"Telegram error for {chat_id}:", e)

    print(f"{stamp}:         ", msg)
