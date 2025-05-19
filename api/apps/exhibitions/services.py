import logging

from starlette.exceptions import HTTPException

from api.apps.exhibitions.models import (
    Exhibition,
    ExhibitionCategory,
    ExhibitionDetails,
    ExhibitionGeo, ExhibitionMeta,
)
from api.apps.exhibitions.schemas import ExhibitionCreate
from api.apps.exhibitions.utils import slugify

logger = logging.getLogger(__name__)


class ExhibitionService:
    def __init__(self, limit: int = 10, offset: int = 0):
        self.limit = limit
        self.offset = offset

    async def get_all(self) -> dict:
        total = await Exhibition.count()
        exhibitions = (
            await Exhibition.objects().prefetch(Exhibition.geo)
            .limit(self.limit)
            .offset(self.offset)
            .order_by(Exhibition.created_at, ascending=False)
        )
        return {
            'total': total,
            'limit': self.limit,
            'offset': self.offset,
            'results': [e.to_dict() for e in exhibitions],
        }

    @staticmethod
    async def create(data: ExhibitionCreate):
        if await Exhibition.select().where(Exhibition.slug == data.slug).first():
            raise HTTPException(status_code=400, detail='Exhibition already exists')

        geo = await ExhibitionGeo.objects().create(
            location=data.geo.location,
            latitude=data.geo.latitude,
            longitude=data.geo.longitude,
            country=data.geo.country,
            city=data.geo.city,
        )

        category_slug = data.category.slug or slugify(data.category.title)
        category = (
            await ExhibitionCategory.select()
            .where(
                ExhibitionCategory.slug == category_slug,
            )
            .first()
        )
        if not category:
            category = await ExhibitionCategory.objects().create(
                title=data.category.title,
                slug=category_slug,
            )

        details = await ExhibitionDetails.objects().create(
            description=data.details.description,
        )

        exhibition = await Exhibition.objects().create(
            title=data.title,
            slug=data.slug,
            short_description=data.short_description,
            category=category['id'],
            details=details['id'],
            geo=geo['id'],
        )

        return {'message': 'Exhibition created', 'exhibition': exhibition.to_dict()}

    @staticmethod
    async def delete(slug: str):
        if not await Exhibition.select().where(Exhibition.slug == slug).first():
            raise HTTPException(status_code=404, detail='Exhibition not found')
        await Exhibition.delete().where(Exhibition.slug == slug)
        return {'message': 'Exhibition deleted', 'exhibition': slug}

    @staticmethod
    async def get_by_slug(slug: str):
        exhibition = await Exhibition.select().where(Exhibition.slug == slug).first()
        if not exhibition:
            raise HTTPException(status_code=404, detail='Exhibition not found')
        return exhibition

    @staticmethod
    async def get_by_category(category_slug: str):
        category = (
            await ExhibitionCategory.select()
            .where(
                ExhibitionCategory.slug == category_slug,
            )
            .first()
        )
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')

        exhibitions = (
            await Exhibition.select()
            .where(
                Exhibition.category == category['id'],
            )
            .order_by(Exhibition.created_at, ascending=False)
        )

        if not exhibitions:
            raise HTTPException(status_code=404, detail='Exhibition not found')

        return exhibitions
