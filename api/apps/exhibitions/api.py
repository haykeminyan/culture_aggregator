import logging

from fastapi import APIRouter, Query

from api.apps.exhibitions.schemas import ExhibitionCreate, ExhibitionUpdate
from api.apps.exhibitions.services import ExhibitionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api', tags=['Exhibitions API'])


@router.get('/')
async def get_all_json(
    limit: int = Query(10),
    offset: int = Query(0),
):
    return await ExhibitionService(limit, offset).get_all()


@router.post('/exhibition')
async def create_api(data: ExhibitionCreate):
    return await ExhibitionService.create(data)

@router.put('/exhibition/{slug}')
async def update_api(slug: str, data: ExhibitionUpdate):
    return await ExhibitionService.update(slug, data)


@router.delete('/exhibitions/{slug}')
async def delete_api(slug: str):
    return await ExhibitionService.delete(slug)


@router.get('/exhibitions/{slug}')
async def get_by_slug_api(slug: str):
    return await ExhibitionService.get_by_slug(slug)


@router.get('/categories/{category_slug}/')
async def get_by_category_api(category_slug: str):
    return await ExhibitionService.get_by_category(category_slug)
