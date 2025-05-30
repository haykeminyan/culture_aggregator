import logging


from api.apps.exhibitions.graphql.types import ExhibitionCreateInput, ExhibitionUpdateInput
from api.apps.exhibitions.models import (
    Exhibition,
    ExhibitionCategory,
    ExhibitionDetail,
    ExhibitionGeo,
)
from api.apps.exhibitions.services import ExhibitionService
from starlette.exceptions import HTTPException

logger = logging.getLogger(__name__)


class ExhibitionServiceGraphQL:
    def __init__(self, limit: int = 10, offset: int = 0):
        self.limit = limit
        self.offset = offset


    @staticmethod
    async def extract_all_data(exhibition: Exhibition) -> dict:
        exhibition_category_full = await ExhibitionCategory.select().where(
            ExhibitionCategory.id == exhibition["exhibition"]["category"]
        ).first()

        exhibition_category = {
            "slug": exhibition_category_full['slug'],
            "title": exhibition_category_full['title'],
        }
        exhibition['exhibition']['category'] = exhibition_category

        exhibition_geo_full = await ExhibitionGeo.select().where(ExhibitionGeo.id == exhibition["exhibition"]["geo"]).first()
        exhibition_geo = {
            'location': exhibition_geo_full['location'],
            'latitude': exhibition_geo_full['latitude'],
            'longitude': exhibition_geo_full['longitude'],
            'country': exhibition_geo_full['country'],
            'city': exhibition_geo_full['city'],
        }
        exhibition['exhibition']['geo'] = exhibition_geo

        exhibition_details_full = await ExhibitionDetail.select().where(ExhibitionDetail.id == exhibition["exhibition"]["details"]).first()
        exhibition_details = {
            'description': exhibition_details_full['description'],
        }
        exhibition['exhibition']['details'] = exhibition_details
        return exhibition

    @staticmethod
    async def create_with_full_data( data: ExhibitionCreateInput):
        exhibition = await ExhibitionService.create(data)
        return await ExhibitionServiceGraphQL.extract_all_data_graphql(exhibition)

    @staticmethod
    async def update(slug: str,  data: ExhibitionUpdateInput):
        exhibition = await ExhibitionService.update(slug, data)
        return await ExhibitionServiceGraphQL.extract_all_data_graphql(exhibition)

    @staticmethod
    async def get_by_slug(slug: str):
        exhibition = await Exhibition.select().where(Exhibition.slug == slug).first()
        exhibition_full = await ExhibitionServiceGraphQL.extract_all_data_graphql({'exhibition': exhibition})
        if not exhibition:
            raise HTTPException(status_code=404, detail='Exhibition not found')
        return exhibition_full

    @staticmethod
    async def get_by_category(category_slug: str):
        exhibition_all = await ExhibitionService.get_by_category(category_slug)
        exhibitions_category = []
        for exhibition in exhibition_all:
            exhibition_full = await ExhibitionServiceGraphQL.extract_all_data_graphql({'exhibition': exhibition})
            exhibitions_category.append(exhibition_full)
        if not exhibitions_category:
            raise HTTPException(status_code=404, detail='Exhibition not found')
        return exhibitions_category