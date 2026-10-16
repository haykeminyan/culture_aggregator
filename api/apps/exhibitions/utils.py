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


def clean_email(value: str | None) -> str:
    """Bare address from a stored contact: drops a 'mailto:' prefix and any '?subject=...' part."""
    if not value:
        return ''
    value = re.sub(r'^\s*mailto:', '', value, flags=re.IGNORECASE)
    return value.split('?', 1)[0].strip()


# the admin form stores this 1.8 MB placeholder when no picture is uploaded;
# pages draw their own placeholder, so it is never worth downloading
PLACEHOLDER_IMAGE = 'default_image.png'


def real_images(images: list[str] | None) -> list[str]:
    return [i for i in (images or []) if i and not i.endswith(PLACEHOLDER_IMAGE)]


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
