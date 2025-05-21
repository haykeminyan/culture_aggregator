import strawberry

from api.apps.exhibitions.graphql.services import ExhibitionServiceGraphQL
from api.apps.exhibitions.graphql.types import Exhibition, ExhibitionCategory, ExhibitionGeo, ExhibitionDetails
from api.apps.exhibitions.services import ExhibitionService
import logging

logger = logging.getLogger(__name__)




@strawberry.type
class Query:
    @strawberry.field
    async def exhibitions(self, limit: int = 10, offset: int = 0) -> list[Exhibition]:
        data = await ExhibitionService(limit, offset).get_all()
        results = []
        for e in data["results"]:
            results.append(Exhibition.from_dict(e))
        return results

    @strawberry.field
    async def get_by_slug(self, slug: str) -> Exhibition:
        data =  await ExhibitionServiceGraphQL.get_by_slug(slug)
        return Exhibition.from_dict(data['exhibition'])

    @strawberry.field
    async def get_by_category(self, slug: str) -> list[Exhibition]:
        data = await ExhibitionServiceGraphQL.get_by_category(slug)
        return [Exhibition.from_dict(elem["exhibition"]) for elem in data]
