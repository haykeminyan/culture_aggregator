from fastapi import Request


from starlette.exceptions import HTTPException
from fastapi import Query
from fastapi import APIRouter

from api.apps.exhibitions.models import Exhibition, ExhibitionGeo, ExhibitionCategory, ExhibitionDetails, \
    ExhibitionTagLink
from api.apps.exhibitions.schemas import ExhibitionCreate
import logging
from fastapi.responses import HTMLResponse

from api.apps.exhibitions.services import get_all_exhibitions, create_exhibition, delete_exhibition, get_exhibition, \
    get_all_exhibitions_by_category
from api.apps.exhibitions.utils import slugify
from api.core.templates import templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Exhibitions API"])


@router.post("/")
async def create_exhibition_api(data: ExhibitionCreate):
    return await create_exhibition(data)


@router.delete("/exhibitions/{slug}")
async def delete_exhibition_api(slug: str):
    return await delete_exhibition(slug)


@router.get("/exhibitions/{slug}")
async def get_exhibition_api(slug: str):
    return await get_exhibition(slug)


@router.get("/categories/{category_slug}/exhibitions")
async def get_all_exhibitions_by_category_api(category_slug: str):
    return await get_all_exhibitions_by_category(category_slug)

@router.get("/exhibitions")
async def get_all_exhibitions_json(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return await get_all_exhibitions(limit, offset)