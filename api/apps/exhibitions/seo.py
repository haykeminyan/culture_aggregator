"""robots.txt and sitemap.xml for search engines."""
from xml.sax.saxutils import escape

import asyncpg
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse, Response

from api.apps.exhibitions.services import get_db_pool
from api.apps.exhibitions.utils import real_images
from api.core.templates import SITE_URL

router = APIRouter(tags=['SEO'])


ROBOTS_TXT = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /admin_api/
Disallow: /docs
Disallow: /redoc
Disallow: /graphql

Sitemap: {SITE_URL}/sitemap.xml
"""


@router.api_route('/robots.txt', methods=['GET', 'HEAD'], include_in_schema=False)
async def robots_txt():
    return PlainTextResponse(ROBOTS_TXT, headers={'Cache-Control': 'public, max-age=86400'})


def _image_url(path: str) -> str:
    if path.startswith(('http://', 'https://')):
        return path
    return f'{SITE_URL}/static/{path.lstrip("/")}'


def _url(loc: str, lastmod=None, changefreq: str = None, priority: str = None, images=()) -> str:
    parts = [f'<loc>{escape(loc)}</loc>']
    if lastmod:
        parts.append(f'<lastmod>{lastmod.isoformat(timespec="seconds")}</lastmod>')
    if changefreq:
        parts.append(f'<changefreq>{changefreq}</changefreq>')
    if priority:
        parts.append(f'<priority>{priority}</priority>')
    for image in images:
        parts.append(f'<image:image><image:loc>{escape(_image_url(image))}</image:loc></image:image>')
    return f'  <url>{"".join(parts)}</url>'


@router.api_route('/sitemap.xml', methods=['GET', 'HEAD'], include_in_schema=False)
async def sitemap_xml(pool: asyncpg.pool.Pool = Depends(get_db_pool)):
    async with pool.acquire() as conn:
        exhibitions = await conn.fetch(
            """
            SELECT e.slug, COALESCE(e.updated_at, e.created_at) AS updated_at, m.images
            FROM exhibition e
            LEFT JOIN exhibition_media m ON e.media = m.id
            WHERE e.is_active = TRUE AND e.slug IS NOT NULL AND e.slug <> ''
            ORDER BY e.start_date DESC
            """
        )
        categories = await conn.fetch(
            """
            SELECT c.slug, MAX(COALESCE(e.updated_at, e.created_at)) AS updated_at
            FROM exhibition_category c
            JOIN exhibition e ON e.category = c.id AND e.is_active = TRUE
            WHERE c.slug IS NOT NULL AND c.slug <> ''
            GROUP BY c.slug
            ORDER BY c.slug
            """
        )

    latest = max((e['updated_at'] for e in exhibitions if e['updated_at']), default=None)
    urls = [_url(f'{SITE_URL}/', latest, 'daily', '1.0')]
    urls += [
        _url(f'{SITE_URL}/?category={c["slug"]}', c['updated_at'], 'daily', '0.7')
        for c in categories
    ]
    urls += [
        _url(
            f'{SITE_URL}/exhibition/{e["slug"]}', e['updated_at'], 'weekly', '0.8',
            real_images(e['images']),
        )
        for e in exhibitions
    ]

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
        ' xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        + '\n'.join(urls)
        + '\n</urlset>\n'
    )
    return Response(
        content=xml,
        media_type='application/xml',
        headers={'Cache-Control': 'public, max-age=3600'},
    )
