#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отправляет короткое HQ-уведомление в штаб-чат.
env:
  TG_BOT_TOKEN (required)
  TG_HQ_CHAT_ID (required)
  PULSE_TEXT (required) — текст сообщения
"""
import os, json, urllib.request, urllib.parse

def send(msg: str) -> None:
    token = os.getenv("TG_BOT_TOKEN", "")
    chat_id = os.getenv("TG_HQ_CHAT_ID", "")
    if not token or not chat_id:
        print("Skip tg_notify: missing TG_BOT_TOKEN or TG_HQ_CHAT_ID")
        return
    api = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": msg,
        "disable_web_page_preview": True,
        "parse_mode": "Markdown",
    }
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(api, data=body)
    with urllib.request.urlopen(req, timeout=10) as r:
        print("tg_notify:", r.status)

if __name__ == "__main__":
    text = os.getenv("PULSE_TEXT", "").strip()
    if text:
        send(text)
    else:
        print("Skip tg_notify: empty PULSE_TEXT")
