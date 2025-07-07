from __future__ import annotations

import re
import time
from datetime import datetime

import pytz
from unidecode import unidecode
import logging

logger = logging.getLogger(__name__)

def now():
    return datetime.now(pytz.UTC)


def slugify(text: str) -> str:
    text = unidecode(text).lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')


def log_duration(label):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start = time.monotonic()
            result = await func(*args, **kwargs)
            elapsed = time.monotonic() - start
            logger.error(f"{label} took {elapsed:.15f} seconds")
            logger.error('!'*10)
            return result
        return wrapper
    return decorator
