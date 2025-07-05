import logging

import asyncpg
from fastapi import APIRouter, Query, Depends

from api.apps.exhibitions.services import ExhibitionService, get_db_pool

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api', tags=['Exhibitions API'])


@router.get('/')
async def get_all_json(
    limit: int = Query(4),
    offset: int = Query(0),
):
    return await ExhibitionService(limit, offset).get_all()


@router.delete('/exhibitions/{slug}')
async def delete_api(slug: str):
    return await ExhibitionService.delete(slug)


@router.get('/exhibitions/{slug}')
async def get_by_slug_api(slug: str, pool: asyncpg.pool.Pool = Depends(get_db_pool)):
    return await ExhibitionService.get_by_slug(slug, pool)


@router.get('/categories/{category_slug}/')
async def get_by_category_api(category_slug: str):
    return await ExhibitionService.get_by_category(category_slug)


@router.get('/filter')
async def get_by_date_api(from_date: str = Query(...), until_date: str = Query(...)):
    return await ExhibitionService.get_exhibition_by_dates(from_date, until_date)
