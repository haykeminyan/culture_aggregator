"""Loads pre-made translations of category and exhibition titles into
`text_translation`, so pages in other languages are translated from the first visit
instead of one page at a time.

The seed is `api/core/translation_seed.json.gz`: {lang: {english text: translation}}.
It was made with Google's keyless web endpoint, so it costs nothing and does not
touch the Azure monthly budget in `translation_usage`. Rows already in the table
win (ON CONFLICT DO NOTHING), and each seed file is loaded only once: its sha1 is
recorded in `translation_seed`, so later deploys skip it in a single query."""
import asyncio
import gzip
import hashlib
import json
import logging
import os

from api.core.machine_translate import _ensure_schema, _hash

logger = logging.getLogger(__name__)

SEED_PATH = os.path.join(os.path.dirname(__file__), 'translation_seed.json.gz')


async def load_translation_seed(pool, path: str = SEED_PATH) -> int:
    """Inserts the seed's rows that are not in the table yet. Returns rows inserted."""
    if not os.path.exists(path):
        return 0
    with open(path, 'rb') as f:
        raw = f.read()
    digest = hashlib.sha1(raw).hexdigest()
    async with pool.acquire() as conn:
        await _ensure_schema(conn)
        await conn.execute(
            'CREATE TABLE IF NOT EXISTS translation_seed ('
            ' sha1 TEXT PRIMARY KEY, loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW())'
        )
        if await conn.fetchval('SELECT 1 FROM translation_seed WHERE sha1 = $1', digest):
            return 0
        seed = json.loads(gzip.decompress(raw))
        before = await conn.fetchval('SELECT COUNT(*) FROM text_translation')
        for lang, pairs in seed.items():
            rows = [(lang, _hash(src, False), dst) for src, dst in pairs.items() if src and dst]
            async with conn.transaction():
                await conn.executemany(
                    'INSERT INTO text_translation (lang, source_hash, translated) VALUES ($1, $2, $3)'
                    ' ON CONFLICT DO NOTHING',
                    rows,
                )
        inserted = await conn.fetchval('SELECT COUNT(*) FROM text_translation') - before
        await conn.execute('INSERT INTO translation_seed (sha1) VALUES ($1) ON CONFLICT DO NOTHING', digest)
    logger.info('translation seed: %s new rows', inserted)
    return inserted


def start_seed_loader(get_pool):
    """Runs the loader in the background so startup isn't held up; never raises."""
    async def run():
        try:
            await load_translation_seed(await get_pool())
        except Exception:
            logger.warning('translation seed failed to load', exc_info=True)
    return asyncio.get_running_loop().create_task(run())
