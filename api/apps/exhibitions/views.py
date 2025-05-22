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
    limit: int = Query(10),
    offset: int = Query(0),
):
    service = ExhibitionService(limit, offset)
    data = await service.get_all()

    exhibitions = data['exhibitions']

    total = data['total']
    limit = data['limit']
    offset = data['offset']

    context = {
        "request": request,
        "exhibitions": exhibitions,
        "categories": await service.get_categories(),
        **ExhibitionService.get_pagination_context(limit, offset, total)
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
async def get_by_category_html(request: Request, category_slug: str,
    limit: int = Query(10),
    offset: int = Query(0),
                               ):
    exhibitions = await ExhibitionService.get_by_category(category_slug)
    total = len(exhibitions)

    context = {
        "exhibitions": exhibitions,
        "request": request,
        "category_slug": category_slug,
        **ExhibitionService.get_pagination_context(limit, offset, total)
    }

    return templates.TemplateResponse('exhibitions/list.html', context)
