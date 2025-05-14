from __future__ import annotations

from datetime import datetime, UTC
import re
from unidecode import unidecode
import pytz

def now():
    return datetime.now(pytz.UTC)



def slugify(text: str) -> str:
    text = unidecode(text).lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

