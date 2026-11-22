"""Exhibition text (titles, categories, descriptions) in the visitor's language.

Translated once through the Google Cloud Translation API (v2, `GOOGLE_TRANSLATE_API_KEY`)
the first time someone opens a page in that language, then served from the
`text_translation` table forever. A monthly character budget
(`GOOGLE_TRANSLATE_MONTHLY_CHARS`, default 500,000 = Google's free tier) stops new
translations once spent; untranslated text simply shows in English until the
next month. Without a key nothing is sent and every page stays as it was."""
import hashlib
import logging
import os
from datetime import date

import aiohttp

from api.core.i18n import DEFAULT_LANG

logger = logging.getLogger(__name__)

API_URL = 'https://translation.googleapis.com/language/translate/v2'
MONTHLY_CHARS = int(os.getenv('GOOGLE_TRANSLATE_MONTHLY_CHARS', '500000'))
BATCH = 100  # the v2 API takes at most 128 strings per request

# Our language codes -> Google's
GOOGLE_CODES = {'pt': 'pt-PT', 'pt-br': 'pt', 'ary': 'ar', 'mwl': 'pt-PT', 'oc-aranes': 'oc'}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS text_translation (
    lang TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    translated TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (lang, source_hash)
);
CREATE TABLE IF NOT EXISTS translation_usage (
    month TEXT PRIMARY KEY,
    chars BIGINT NOT NULL DEFAULT 0
);
"""
_schema_ready = False


def _key() -> str:
    return os.getenv('GOOGLE_TRANSLATE_API_KEY', '').strip()


def _hash(text: str, html: bool) -> str:
    return hashlib.sha1((('h:' if html else 't:') + text).encode()).hexdigest()


async def _ensure_schema(conn):
    global _schema_ready
    if not _schema_ready:
        await conn.execute(_SCHEMA)
        _schema_ready = True


async def _reserve(conn, wanted: int) -> int:
    """Claims up to `wanted` characters of this month's budget, returns how many."""
    month = date.today().strftime('%Y-%m')
    async with conn.transaction():
        await conn.execute(
            'INSERT INTO translation_usage (month) VALUES ($1) ON CONFLICT DO NOTHING', month
        )
        used = await conn.fetchval('SELECT chars FROM translation_usage WHERE month = $1 FOR UPDATE', month)
        granted = max(0, min(wanted, MONTHLY_CHARS - used))
        if granted:
            await conn.execute('UPDATE translation_usage SET chars = chars + $2 WHERE month = $1', month, granted)
    return granted


async def _google(texts: list[str], lang: str, html: bool) -> list[str]:
    out = []
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
        for i in range(0, len(texts), BATCH):
            payload = {
                'q': texts[i:i + BATCH], 'target': GOOGLE_CODES.get(lang, lang),
                'source': 'en', 'format': 'html' if html else 'text',
            }
            async with session.post(API_URL, params={'key': _key()}, json=payload) as r:
                r.raise_for_status()
                data = await r.json()
            out += [t['translatedText'] for t in data['data']['translations']]
    return out


async def translate_texts(pool, lang: str, texts: list, html: bool = False) -> list:
    """Same list back, with every string it can translate translated. Never raises."""
    if lang == DEFAULT_LANG or not any(texts):
        return list(texts)
    unique = list(dict.fromkeys(t for t in texts if t and t.strip()))
    hashes = {t: _hash(t, html) for t in unique}
    try:
        async with pool.acquire() as conn:
            await _ensure_schema(conn)
            rows = await conn.fetch(
                'SELECT source_hash, translated FROM text_translation WHERE lang = $1 AND source_hash = ANY($2)',
                lang, list(hashes.values()),
            )
            done = {r['source_hash']: r['translated'] for r in rows}
            missing = [t for t in unique if hashes[t] not in done]
            if missing and _key():
                budget = await _reserve(conn, sum(len(t) for t in missing))
                todo, size = [], 0
                for t in missing:
                    if size + len(t) > budget:
                        break
                    todo.append(t)
                    size += len(t)
                if size < budget:  # give back what this batch won't use
                    await conn.execute(
                        'UPDATE translation_usage SET chars = chars - $2 WHERE month = $1',
                        date.today().strftime('%Y-%m'), budget - size,
                    )
                if todo:
                    translated = await _google(todo, lang, html)
                    await conn.executemany(
                        'INSERT INTO text_translation (lang, source_hash, translated) VALUES ($1, $2, $3)'
                        ' ON CONFLICT DO NOTHING',
                        [(lang, hashes[s], t) for s, t in zip(todo, translated)],
                    )
                    done.update({hashes[s]: t for s, t in zip(todo, translated)})
    except Exception:
        logger.exception('machine translation failed for %s', lang)
        return list(texts)
    return [done.get(hashes.get(t), t) if t else t for t in texts]


async def translate_fields(pool, lang: str, rows: list, fields: tuple, html: bool = False):
    """Translates the given keys of each dict in place."""
    if lang == DEFAULT_LANG or not rows:
        return rows
    flat = [row.get(f) for row in rows for f in fields]
    out = await translate_texts(pool, lang, flat, html)
    it = iter(out)
    for row in rows:
        for f in fields:
            row[f] = next(it)
    return rows
