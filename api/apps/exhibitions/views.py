from urllib import request

from fastapi import Request


from fastapi import Query
from fastapi import APIRouter

from api.apps.exhibitions.schemas import ExhibitionCreate
import logging
from fastapi.responses import HTMLResponse

from api.apps.exhibitions.services import get_all_exhibitions, delete_exhibition, create_exhibition, get_exhibition, \
    get_all_exhibitions_by_category
from api.core.templates import templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Exhibitions Views"])

@router.post("/", response_class=HTMLResponse, include_in_schema=False)
async def create_exhibition_html(request: Request, data: ExhibitionCreate):
    context = await create_exhibition(data)
    context['request'] = request
    return templates.TemplateResponse("exhibitions/body.html", context)

@router.delete("/exhibitions/{slug}", response_class=HTMLResponse, include_in_schema=False)
async def delete_exhibition_html(request: Request, slug: str):
    context = await delete_exhibition(slug)
    context['request'] = request
    return templates.TemplateResponse("exhibitions/body.html", context)

@router.get("/exhibitions/{slug}", response_class=HTMLResponse, include_in_schema=False)
async def get_exhibition_html(request: Request, slug: str):
    context = await get_exhibition(slug)
    context['request'] = request
    return templates.TemplateResponse("exhibitions/body.html", context)

@router.get("/categories/{category_slug}/exhibitions", response_class=HTMLResponse, include_in_schema=False)
async def get_all_exhibitions_by_category_html(category_slug: str):
    context =  await get_all_exhibitions_by_category(category_slug)
    context['request'] = request
    return templates.TemplateResponse("exhibitions/body.html", context)

@router.get("/exhibitions", response_class=HTMLResponse, include_in_schema=False)
async def get_all_exhibitions_html(
        request: Request,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    context = await get_all_exhibitions(limit, offset)
    context['request'] = request
    return templates.TemplateResponse("exhibitions/body.html", context)