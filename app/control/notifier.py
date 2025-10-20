# app/control/notifier.py
from __future__ import annotations

import os
import logging
from typing import Optional

import aiohttp
from aiogram import Bot

try:
    import sentry_sdk
except Exception:  # sentry optional
    sentry_sdk = None  # type: ignore

ADMIN_ALERT_CHAT_ID = os.getenv("ADMIN_ALERT_CHAT_ID")
CRONITOR_PING_URL = os.getenv("CRONITOR_PING_URL")  # e.g. https://cronitor.link/p/xxxx/beat

async def notify_admins(bot: Bot, text: str) -> int:
    """Send a message to ADMIN_ALERT_CHAT_ID if set; mirror to Sentry & Cronitor."""
    sent = 0
    if ADMIN_ALERT_CHAT_ID:
        try:
            await bot.send_message(int(ADMIN_ALERT_CHAT_ID), text)
            sent += 1
        except Exception as e:
            logging.warning("notify_admins: telegram send failed: %s", e)

    if sentry_sdk:
        try:
            sentry_sdk.capture_message(text)
        except Exception as e:
            logging.debug("notify_admins: sentry capture failed: %s", e)

    if CRONITOR_PING_URL:
        try:
            async with aiohttp.ClientSession() as s:
                await s.get(CRONITOR_PING_URL, timeout=5)
        except Exception as e:
            logging.debug("notify_admins: cronitor ping failed: %s", e)

    return sent
