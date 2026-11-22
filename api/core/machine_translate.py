"""Exhibition text (titles, categories, descriptions) in the visitor's language.

Translated once, the first time someone opens a page in that language, then served
from the `text_translation` table forever. Engines, first one configured wins:
Azure Translator (`AZURE_TRANSLATOR_KEY`, `AZURE_TRANSLATOR_REGION`), the Google
Cloud Translation API (`GOOGLE_TRANSLATE_API_KEY`), else Google's keyless web
endpoint. A monthly character budget (`TRANSLATE_MONTHLY_CHARS`; defaults to the free
tier: 2,000,000 with Azure, 500,000 otherwise) stops new translations once spent;
untranslated text shows in English until the next month."""
import asyncio
import hashlib
import re
import time
import logging
import os
from datetime import date

import aiohttp

from api.core.i18n import DEFAULT_LANG

logger = logging.getLogger(__name__)

API_URL = 'https://translation.googleapis.com/language/translate/v2'
AZURE_URL = 'https://api.cognitive.microsofttranslator.com/translate'
# free tiers: Azure F0 = 2,000,000 characters a month, Google = 500,000
MONTHLY_CHARS = int(
    os.getenv('TRANSLATE_MONTHLY_CHARS')
    or os.getenv('GOOGLE_TRANSLATE_MONTHLY_CHARS')
    or ('2000000' if os.getenv('AZURE_TRANSLATOR_KEY', '').strip() else '500000')
)
# Our language codes -> Azure's; Azure has no Occitan, so Aranés goes through Google
AZURE_CODES = {'pt': 'pt-pt', 'pt-br': 'pt', 'ary': 'ar', 'mwl': 'pt-pt', 'oc-aranes': None}
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


FREE_URL = 'https://translate.googleapis.com/translate_a/single'
_TAG = re.compile(r'(<[^>]+>|&[#\w]+;)')


async def _free_one(session, text: str, target: str) -> str:
    params = {'client': 'gtx', 'sl': 'en', 'tl': target, 'dt': 't', 'q': text}
    async with session.post(FREE_URL, data=params, allow_redirects=False) as r:
        if r.status != 200:  # 302 to google.com/sorry or 429 means we're throttled
            raise RuntimeError(f'free translate endpoint answered {r.status}')
        data = await r.json(content_type=None)
    return ''.join(part[0] for part in data[0] if part and part[0])


async def _free(texts: list[str], lang: str, html: bool) -> list[str]:
    """Google's keyless web endpoint: no account or cost, but unofficial and
    rate-limited, so requests go out a few at a time. HTML is split so only the
    text between tags is sent."""
    target = GOOGLE_CODES.get(lang, lang)
    gate = asyncio.Semaphore(4)

    async def one(text):
        async with gate:
            return await _free_one(session, text, target)

    async def translate(text):
        if not html:
            return await one(text)
        parts = _TAG.split(text)
        jobs = [one(p) if i % 2 == 0 and p.strip() else None for i, p in enumerate(parts)]
        done = await asyncio.gather(*(j for j in jobs if j))
        it = iter(done)
        return ''.join(next(it) if j else p for j, p in zip(jobs, parts))

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        return list(await asyncio.gather(*(translate(t) for t in texts)))


_paused_until = 0.0
PAUSE = 15 * 60  # after a throttle, leave the keyless endpoint alone for a while


async def _azure(texts: list[str], lang: str, html: bool) -> list[str]:
    headers = {'Ocp-Apim-Subscription-Key': os.getenv('AZURE_TRANSLATOR_KEY', '').strip()}
    region = os.getenv('AZURE_TRANSLATOR_REGION', '').strip()
    if region:
        headers['Ocp-Apim-Subscription-Region'] = region
    params = {'api-version': '3.0', 'from': 'en', 'to': AZURE_CODES.get(lang, lang),
              'textType': 'html' if html else 'plain'}
    out = []
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
        # at most 1000 strings and 50,000 characters per request
        batch, size = [], 0
        for text in texts + [None]:
            if text is None or len(batch) == 100 or size + len(text) > 45_000:
                if batch:
                    async with session.post(AZURE_URL, params=params, headers=headers,
                                            json=[{'Text': t} for t in batch]) as r:
                        if r.status != 200:
                            raise RuntimeError(f'Azure Translator answered {r.status}: {await r.text()}')
                        out += [item['translations'][0]['text'] for item in await r.json()]
                batch, size = [], 0
            if text is not None:
                batch.append(text)
                size += len(text)
    return out


async def _google(texts: list[str], lang: str, html: bool) -> list[str]:
    global _paused_until
    if os.getenv('AZURE_TRANSLATOR_KEY', '').strip() and AZURE_CODES.get(lang, lang):
        return await _azure(texts, lang, html)
    if not _key():
        if time.monotonic() < _paused_until:
            raise RuntimeError('keyless translation paused after throttling')
        try:
            return await _free(texts, lang, html)
        except Exception:
            _paused_until = time.monotonic() + PAUSE
            raise
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
            if missing:
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
                    try:
                        translated = await _google(todo, lang, html)
                    except Exception:  # nothing was translated, so nothing is spent
                        await conn.execute(
                            'UPDATE translation_usage SET chars = chars - $2 WHERE month = $1',
                            date.today().strftime('%Y-%m'), size,
                        )
                        raise
                    await conn.executemany(
                        'INSERT INTO text_translation (lang, source_hash, translated) VALUES ($1, $2, $3)'
                        ' ON CONFLICT DO NOTHING',
                        [(lang, hashes[s], t) for s, t in zip(todo, translated)],
                    )
                    done.update({hashes[s]: t for s, t in zip(todo, translated)})
    except Exception:
        logger.warning('machine translation failed for %s', lang, exc_info=True)
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
