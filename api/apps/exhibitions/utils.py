from __future__ import annotations

import re
from datetime import datetime

import pytz
from unidecode import unidecode


def now():
    return datetime.now(pytz.UTC)


def slugify(text: str) -> str:
    text = unidecode(text).lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')
