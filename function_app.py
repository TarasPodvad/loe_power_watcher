import json
import logging
import os
from datetime import datetime

import azure.functions as func
from azure.core.exceptions import ResourceExistsError
from azure.storage.queue import QueueClient, TextBase64EncodePolicy

import watcher
from config import now
from storage import get_text
from telegramer import send_telegram

app = func.FunctionApp()
QUEUE = "loe-alerts"


def _queue() -> QueueClient:
    q = QueueClient.from_connection_string(
        os.environ["AzureWebJobsStorage"], QUEUE, message_encode_policy=TextBase64EncodePolicy()
    )
    try:
        q.create_queue()
    except ResourceExistsError:
        pass
    return q


def _enqueue(send_at, version, event_id, text):
    # queue message stays invisible until send_at (max 7 days) -> fires on time
    delay = max(0, int((send_at - now()).total_seconds()))
    body = {"version": version, "event_id": event_id, "text": text,
            "event_at": event_id.split("_")[0] + " " + event_id.split("_")[2]}
    _queue().send_message(json.dumps(body, ensure_ascii=False), visibility_timeout=delay, time_to_live=delay + 3600)


@app.timer_trigger(schedule="0 */10 * * * *", arg_name="timer", run_on_startup=False)
def check_schedule(timer: func.TimerRequest) -> None:
    logging.info("check_schedule: %s", watcher.check(_enqueue))


@app.queue_trigger(arg_name="msg", queue_name=QUEUE, connection="AzureWebJobsStorage")
def send_alert(msg: func.QueueMessage) -> None:
    data = json.loads(msg.get_body().decode())
    if get_text("version.txt") != data["version"]:
        logging.info("stale alert skipped: %s", data["event_id"])
        return
    if datetime.strptime(data["event_at"], "%Y-%m-%d %H:%M") <= now():
        logging.info("late alert skipped: %s", data["event_id"])
        return
    send_telegram(data["text"])
