import logging
from urllib.parse import urlencode
from typing import Optional
from datetime import datetime

import asyncpg
from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from api.apps.exhibitions.schemas import ExhibitionCreate
from api.apps.exhibitions.services import ExhibitionService, get_db_pool
from api.apps.exhibitions.utils import real_images
from api.core.i18n import localize, request_lang
from api.core.machine_translate import translate_fields
from api.core.templates import templates
from asyncio import gather

logger = logging.getLogger(__name__)

router = APIRouter(prefix='', tags=['Exhibitions Views'])

PAGE_SIZE = 12


def _legacy_page_redirect(request: Request):
    """Old links used ?limit=&offset=; they move for good to ?page=N, other filters kept."""
    qp = request.query_params
    if 'limit' not in qp and 'offset' not in qp:
        return None
    try:  # the page that holds the first exhibition the old link showed
        page = max(0, int(qp.get('offset') or 0)) // PAGE_SIZE + 1
    except ValueError:
        page = 1
    params = [(k, v) for k, v in qp.multi_items() if k not in ('limit', 'offset', 'page')]
    if page > 1:
        params.append(('page', str(page)))
    query = urlencode(params)
    return RedirectResponse(localize(request.url.path, request_lang(request)) + ('?' + query if query else ''),
                            status_code=301)


@router.get('/', response_class=HTMLResponse, include_in_schema=False)
async def get_all_html(
    request: Request,
    pool: asyncpg.pool.Pool = Depends(get_db_pool),
    search: str = Query('', alias='search'),
    country: Optional[list[str]] = Query(default=[]),
    city: Optional[list[str]] = Query(default=[]),
    category: Optional[str] = Query(None),
    from_date: datetime = Query(None),
    until_date: datetime = Query(None),
    page: int = Query(1),
):
    if redirect := _legacy_page_redirect(request):
        return redirect
    limit, offset = PAGE_SIZE, (max(page, 1) - 1) * PAGE_SIZE
    service = ExhibitionService(limit, offset, search)

    # фильтрация по множеству
    exhibitions, total = await service.get_filtered(
        pool=pool,
        search=search,
        countries=country,
        cities=city,
        categories=category,
        from_date=from_date,
        until_date=until_date,
        offset=offset,
        limit=limit,
    )

    for e in exhibitions:
        e['images'] = real_images(e.get('images'))

    categories, countries, cities = await gather(
        service.get_categories(pool=pool),
        service.get_countries(pool=pool),
        service.get_cities(pool=pool),
    )

    lang = request_lang(request)
    await gather(
        translate_fields(pool, lang, exhibitions, ('title', 'short_description', 'category_title')),
        translate_fields(pool, lang, categories, ('title',)),
    )

    context = {
        'request': request,
        'exhibitions': exhibitions,
        'categories': categories,
        'selected_category': category,
        'countries': countries,
        'selected_country': country,
        'cities': cities,
        'selected_city': city,
        'search': search,
        **ExhibitionService.get_pagination_context(limit, offset, total),
    }

    return templates.TemplateResponse(request=request, name='exhibitions/list.html', context=context)


@router.delete('/exhibitions/{slug}', response_class=HTMLResponse, include_in_schema=False)
async def delete_html(request: Request, slug: str):
    context = await ExhibitionService.delete(slug)
    context['request'] = request
    return templates.TemplateResponse(request=request, name='exhibitions/body.html', context=context)


@router.get('/exhibition/{slug}', response_class=HTMLResponse, include_in_schema=False)
async def get_by_slug_html(request: Request, slug: str, pool: asyncpg.pool.Pool = Depends(get_db_pool)):
    context, related = await gather(
        ExhibitionService.get_by_slug(slug, pool),
        ExhibitionService.get_related(slug, pool),
    )
    context['images'] = real_images(context.get('images'))
    lang = request_lang(request)
    await gather(
        translate_fields(pool, lang, [context], ('title',)),
        translate_fields(pool, lang, [context], ('description',), html=True),
        translate_fields(pool, lang, related, ('title', 'category_title')),
    )
    context['related'] = related
    context['request'] = request
    return templates.TemplateResponse(request=request, name='exhibitions/detail.html', context=context)
