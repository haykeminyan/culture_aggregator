import logging

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from api.apps.exhibitions.schemas import ExhibitionCreate
from api.apps.exhibitions.services import ExhibitionService
from api.core.templates import templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix='', tags=['Exhibitions Views'])


@router.get('/', response_class=HTMLResponse, include_in_schema=False)
async def get_all_html(
    request: Request,
    search: str = Query('', alias='search'),
    limit: int = Query(4),
    offset: int = Query(0),
):
    service = ExhibitionService(limit, offset, search)
    data = await service.get_all()

    context = {
        'request': request,
        'exhibitions': data['exhibitions'],
        'categories': await service.get_categories(),
        'countries': await service.get_countries(),
        'cities': await service.get_cities(),
        'search': search,
        **ExhibitionService.get_pagination_context(limit, offset, data['total']),
    }

    return templates.TemplateResponse('exhibitions/list.html', context)


@router.post('/exhibition', response_class=HTMLResponse, include_in_schema=False)
async def create_html(request: Request, data: ExhibitionCreate):
    context = await ExhibitionService.create(data)
    context['request'] = request
    return templates.TemplateResponse('exhibitions/body.html', context)


@router.delete('/exhibitions/{slug}', response_class=HTMLResponse, include_in_schema=False)
async def delete_html(request: Request, slug: str):
    context = await ExhibitionService.delete(slug)
    context['request'] = request
    return templates.TemplateResponse('exhibitions/body.html', context)


@router.get('/exhibition/{slug}', response_class=HTMLResponse, include_in_schema=False)
async def get_by_slug_html(request: Request, slug: str):
    context = await ExhibitionService.get_by_slug(slug)
    context['request'] = request
    return templates.TemplateResponse('exhibitions/detail.html', context)


@router.get(
    '/categories/{category_slug}/',
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def get_by_category_html(
    request: Request,
    category_slug: str,
    limit: int = Query(4),
    offset: int = Query(0),
    search: str = Query('', alias='search'),
):
    exhibitions = await ExhibitionService.get_by_category(category_slug)
    categories = await ExhibitionService.get_categories()
    if search:
        exhibitions = [e for e in exhibitions if search.lower() in e['title'].lower()]

    total = len(exhibitions)
    paginated_exhibitions = exhibitions[offset : offset + limit]

    context = {
        'exhibitions': paginated_exhibitions,
        'request': request,
        'categories': categories,
        'category_slug': category_slug,
        'search': search,
        **ExhibitionService.get_pagination_context(limit, offset, total),
    }

    return templates.TemplateResponse('exhibitions/list.html', context)

@router.get(
    '/country/{country}/',
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def get_by_country_html(
    request: Request,
    country: str,
    limit: int = Query(4),
    offset: int = Query(0),
    search: str = Query('', alias='search'),
):
    exhibitions = await ExhibitionService.get_by_country(country)
    countries = await ExhibitionService.get_countries()

    if search:
        exhibitions = [e for e in exhibitions if search.lower() in e['title'].lower()]

    total = len(exhibitions)
    paginated_exhibitions = exhibitions[offset : offset + limit]

    context = {
        'exhibitions': paginated_exhibitions,
        'request': request,
        'countries': countries,
        'search': search,
        **ExhibitionService.get_pagination_context(limit, offset, total),
    }
    return templates.TemplateResponse('exhibitions/list.html', context)

@router.get(
    '/city/{city}/',
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def get_by_city_html(
    request: Request,
    city: str,
    limit: int = Query(4),
    offset: int = Query(0),
    search: str = Query('', alias='search'),
):
    exhibitions = await ExhibitionService.get_by_city(city)
    cities = await ExhibitionService.get_cities()

    if search:
        exhibitions = [e for e in exhibitions if search.lower() in e['title'].lower()]

    total = len(exhibitions)
    paginated_exhibitions = exhibitions[offset : offset + limit]

    context = {
        'exhibitions': paginated_exhibitions,
        'request': request,
        'cities': cities,
        'search': search,
        **ExhibitionService.get_pagination_context(limit, offset, total),
    }
    return templates.TemplateResponse('exhibitions/list.html', context)

@router.get('/filter', response_class=HTMLResponse, include_in_schema=False)
async def get_by_date_api(
    request: Request,
    from_date: str = Query(...),
    until_date: str = Query(...),
    limit: int = Query(4),
    offset: int = Query(0),
):
    exhibitions = await ExhibitionService.get_exhibition_by_dates(from_date, until_date)
    total = len(exhibitions)
    paginated_exhibitions = exhibitions[offset : offset + limit]

    context = {
        'request': request,
        'exhibitions': paginated_exhibitions,
        'from_date': from_date,
        'until_date': until_date,
        **ExhibitionService.get_pagination_context(limit, offset, total),
    }

    return templates.TemplateResponse('exhibitions/list.html', context)
