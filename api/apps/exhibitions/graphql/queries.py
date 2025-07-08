import logging
from datetime import datetime

import asyncpg
import dateparser
import strawberry
from fastapi import Depends

from api.apps.exhibitions.graphql.services import ExhibitionServiceGraphQL
from api.apps.exhibitions.graphql.types import Exhibition, ExhibitionDetail
from api.apps.exhibitions.services import ExhibitionService
from strawberry.types import Info

logger = logging.getLogger(__name__)


@strawberry.type
class Query:
    @strawberry.field
    async def exhibitions(self, limit: int = 10, offset: int = 0) -> list[Exhibition]:
        data = await ExhibitionService(limit, offset).get_all()
        results = []
        for e in data['results']:
            results.append(Exhibition.from_dict(e))
        return results

    @strawberry.field
    async def get_by_slug(self, info: Info, slug: str) -> ExhibitionDetail:
        pool: asyncpg.pool.Pool = info.context["pool"]

        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM exhibition e left join exhibition_detail e_d on e.id = e_d.id left join exhibition_geo e_g on e.id = e_g.id WHERE slug = $1 ", slug)

        if not row:
            raise Exception("Not found")
        data = dict(row)

        logger.error(data)
        return ExhibitionDetail.from_dict(data)

    @strawberry.field
    async def get_by_category(self, slug: str) -> list[Exhibition]:
        data = await ExhibitionServiceGraphQL.get_by_category(slug)
        return [Exhibition.from_dict(elem['exhibition']) for elem in data]
