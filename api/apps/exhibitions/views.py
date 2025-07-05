import logging
from typing import Optional
from datetime import datetime

import asyncpg
from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import HTMLResponse

from api.apps.exhibitions.schemas import ExhibitionCreate
from api.apps.exhibitions.services import ExhibitionService, get_db_pool
from api.core.templates import templates
from asyncio import gather

logger = logging.getLogger(__name__)

router = APIRouter(prefix='', tags=['Exhibitions Views'])


@router.get('/', response_class=HTMLResponse, include_in_schema=False)
async def get_all_html(
    request: Request,
    search: str = Query('', alias='search'),
    country: Optional[list[str]] = Query(default=[]),
    city: Optional[list[str]] = Query(default=[]),
    category: Optional[str] = Query(None),
    from_date: datetime = Query(None),
    until_date: datetime = Query(None),
    limit: int = Query(4),
    offset: int = Query(0),
):
    service = ExhibitionService(limit, offset, search)

    # фильтрация по множеству
    exhibitions, total = await service.get_filtered(
        search=search,
        countries=country,
        cities=city,
        categories=category,
        from_date=from_date,
        until_date=until_date,
        offset=offset,
        limit=limit,
    )
    categories, countries, cities = await gather(
        service.get_categories(),
        service.get_countries(),
        service.get_cities(),
    )
    logger.error(f"selected_country in context: {country} ({type(country)})")
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

    return templates.TemplateResponse('exhibitions/list.html', context)


@router.delete('/exhibitions/{slug}', response_class=HTMLResponse, include_in_schema=False)
async def delete_html(request: Request, slug: str):
    context = await ExhibitionService.delete(slug)
    context['request'] = request
    return templates.TemplateResponse('exhibitions/body.html', context)


@router.get('/exhibition/{slug}', response_class=HTMLResponse, include_in_schema=False)
async def get_by_slug_html(request: Request, slug: str, pool: asyncpg.pool.Pool = Depends(get_db_pool)):
    context = await ExhibitionService.get_by_slug(slug, pool)
    context['request'] = request
    return templates.TemplateResponse('exhibitions/detail.html', context)
