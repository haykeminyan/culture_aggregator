import json
import logging
from datetime import datetime
from datetime import datetime, timezone, timedelta
import asyncio

from fastapi import Query
from starlette.exceptions import HTTPException

from api.apps.exhibitions.models import (
    Exhibition,
    ExhibitionCategory,
    ExhibitionDetails,
    ExhibitionGeo, ExhibitionMeta, ExhibitionMedia, ExhibitionPeriod,
)
from api.apps.exhibitions.schemas import ExhibitionCreate, ExhibitionUpdate
from api.apps.exhibitions.utils import slugify

logger = logging.getLogger(__name__)


class ExhibitionService:
    def __init__(self, limit: int = 10, offset: int = 0, search: str = ""):
        self.limit = limit
        self.offset = offset
        self.search = search

    async def get_all(self) -> dict:
        # Фильтр по поиску
        filter_ = Exhibition.title.ilike(f"%{self.search}%") if self.search else None

        # Получаем общее количество записей
        count_query = Exhibition.select(Exhibition.id)
        if filter_:
            count_query = count_query.where(filter_)
        total = len(await count_query.run())


        # Загружаем записи с фильтром и пагинацией
        query = (
            Exhibition.objects()
            .order_by(Exhibition.created_at, ascending=False)
            .prefetch(
                Exhibition.geo,
                Exhibition.category,
                Exhibition.details,
                Exhibition.contacts,
                Exhibition.media
            )
        )
        if filter_:
            query = query.where(filter_)
        exhibitions = await query.offset(self.offset).limit(self.limit)

        # Преобразование в список словарей
        result = [
            {
                **e.to_dict(),
                "images": e.media["images"] if isinstance(e.media and e.media["images"],
                                                                      str) else e.media["images"]
            }
            for e in exhibitions
        ]

        for elem in result:
            exhibition_time = await ExhibitionPeriod.select().where(ExhibitionPeriod.exhibition == elem['id'])
            elem['period'] = exhibition_time
        logger.error(result)

        return {
            "total": total,
            "limit": self.limit,
            "offset": self.offset,
            "exhibitions": result,
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
    async def update(slug: str, data: ExhibitionUpdate):
        existing = await Exhibition.select().where(Exhibition.slug == slug).first()
        if not existing:
            raise HTTPException(status_code=404, detail="Exhibition not found")

        category_slug = data.category.slug or slugify(data.category.title)
        category = await ExhibitionCategory.select().where(
            ExhibitionCategory.slug == category_slug
        ).first()

        if not category:
            category = await ExhibitionCategory.objects().create(
                title=data.category.title,
                slug=category_slug,
            )

        geo = await ExhibitionGeo.objects().create(
            location=data.geo.location,
            latitude=data.geo.latitude,
            longitude=data.geo.longitude,
            country=data.geo.country,
            city=data.geo.city,
        )

        # Создание details
        details = await ExhibitionDetails.objects().create(
            description=data.details.description,
        )

        update_data = {
            Exhibition.title: data.title,
            Exhibition.updated_at: datetime.now(),
            Exhibition.short_description: data.short_description,
            Exhibition.category: category["id"],
            Exhibition.geo: geo["id"],
            Exhibition.details: details["id"],
        }

        await Exhibition.update(update_data).where(Exhibition.slug == slug)

        # Загружаем новый slug (если был обновлён)
        updated_slug = data.slug if getattr(data, "slug", None) else slug
        updated_exhibition = await Exhibition.select().where(Exhibition.slug == updated_slug).first()

        return {
            "message": "Exhibition updated",
            "exhibition": updated_exhibition
        }

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
        images_task = ExhibitionService.fill_exhibition_with_images(exhibition)
        details_task = ExhibitionService.fill_exhibition_with_details(exhibition)
        geo_task = ExhibitionService.fill_exhibition_with_geo(exhibition)
        results = await asyncio.gather(images_task, details_task, geo_task)

        for updated in results:
            exhibition.update(updated)
        logger.error(exhibition)
        return exhibition

    # the main problem is that exhibition with relations 1:N contains id
    # and I need to add values
    @staticmethod
    async def fill_exhibition_with_images(exhibition: dict) -> dict:
        images = await ExhibitionMedia.select().where(ExhibitionMedia.id==exhibition['media']).first()
        exhibition['images'] = images['images']
        return exhibition

    @staticmethod
    async def fill_exhibition_with_details(exhibition: dict) -> dict:
        details =  await ExhibitionDetails.select().where(ExhibitionDetails.id == exhibition['details']).first()
        exhibition['details'] = details['description']
        return exhibition

    @staticmethod
    async def fill_exhibition_with_geo(exhibition: dict) -> dict:
        geo =  await ExhibitionGeo.select().where(ExhibitionGeo.id == exhibition['geo']).first()
        exhibition['location'] = geo['location']
        exhibition['latitude'] = geo['latitude']
        exhibition['longitude'] = geo['longitude']
        exhibition['country'] = geo['country']
        exhibition['city'] = geo['city']
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
        filled_exhibitions = []
        for elem in exhibitions:
            filled = await ExhibitionService.fill_exhibition_with_images(elem)
            filled_exhibitions.append(filled)
        return filled_exhibitions

    @staticmethod
    async def get_categories():
        categories = list(set(await ExhibitionCategory.objects()))
        categories.sort(key=lambda c: c.title, reverse=False)
        return categories

    @staticmethod
    async def format_dates(context):
        dates_all = await ExhibitionPeriod.select().where(ExhibitionPeriod.exhibition == context['id'])
        date_pairs = []

        if dates_all:
            sorted_dates = sorted(dates_all, key=lambda d: d['end_date'], reverse=True)

            for elem in sorted_dates:
                start = datetime.fromisoformat(str(elem['start_date'])).strftime("%d %B %Y at %H:%M")
                end = datetime.fromisoformat(str(elem['end_date'])).strftime("%d %B %Y at %H:%M")
                date_pairs.append((start, end))

        context['date_pairs'] = date_pairs
        return context

    @staticmethod
    def get_pagination_context(limit: int, offset: int, total: int):
        return {
            "limit": limit,
            "offset": offset,
            "total": total,
            "next_offset": offset + limit if offset + limit < total else None,
            "prev_offset": offset - limit if offset - limit >= 0 else None,
        }

    @staticmethod
    async def get_exhibition_by_dates(from_date: str = Query(...), until_date: str = Query(...)):
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            until_date = datetime.strptime(until_date, '%Y-%m-%d').replace(tzinfo=timezone.utc) + timedelta(days=1)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        if from_date > until_date:
            from_date, until_date = until_date, from_date

        all_exhibitions = await Exhibition.objects().where(Exhibition.created_at >= from_date).where(
            Exhibition.created_at <= until_date)
        filled_exhibitions = []
        for elem in all_exhibitions:
            filled = await ExhibitionService.fill_exhibition_with_images(elem)
            filled_exhibitions.append(filled)
        return filled_exhibitions
