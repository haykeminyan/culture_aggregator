import logging
from datetime import datetime, timedelta, timezone

from fastapi import Query
from starlette.exceptions import HTTPException

from api.apps.exhibitions.models import Exhibition, ExhibitionCategory

logger = logging.getLogger(__name__)


class ExhibitionService:
    def __init__(self, limit: int = 10, offset: int = 0, search: str = ''):
        self.limit = limit
        self.offset = offset
        self.search = search

    async def get_all(self) -> dict:
        # Фильтр по поиску
        filter_ = Exhibition.title.ilike(f'%{self.search}%') if self.search else None

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
                Exhibition.detail,
                Exhibition.contact,
                Exhibition.media,
            )
        )
        if filter_:
            query = query.where(filter_)
        exhibitions = await query.offset(self.offset).limit(self.limit)

        result = [
            {
                **e.to_dict(),
                'images': (
                    e.media['images']
                    if isinstance(
                        e.media and e.media['images'],
                        str,
                    )
                    else e.media['images']
                ),
            }
            for e in exhibitions
        ]

        await ExhibitionService.insert_format_dates(context=result)

        return {
            'total': total,
            'limit': self.limit,
            'offset': self.offset,
            'exhibitions': result,
        }

    @staticmethod
    async def delete(slug: str):
        if not await Exhibition.select().where(Exhibition.slug == slug).first():
            raise HTTPException(status_code=404, detail='Exhibition not found')
        await Exhibition.delete().where(Exhibition.slug == slug)
        return {'message': 'Exhibition deleted', 'exhibition': slug}

    @staticmethod
    async def get_by_slug(slug: str):
        exhibition = await (
            Exhibition.objects()
            .where(Exhibition.slug == slug)
            .prefetch(
                Exhibition.contact,
                Exhibition.media,
                Exhibition.geo,
            )
            .first()
        )
        if not exhibition:
            raise HTTPException(status_code=404, detail='Exhibition not found')

        await ExhibitionService.format_dates(context=exhibition)

        return await ExhibitionService.insert_pictures(exhibition)

    @staticmethod
    async def get_by_category(category_slug: str):
        category = (
            await ExhibitionCategory.objects()
            .where(ExhibitionCategory.slug == category_slug)
            .first()
        )
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')

        exhibitions = (
            await Exhibition.objects()
            .where(Exhibition.category == category['id'])
            .prefetch(Exhibition.media, Exhibition.geo)
        )
        await ExhibitionService.insert_format_dates(context=exhibitions)

        return [await ExhibitionService.insert_pictures(e) for e in exhibitions]

    @staticmethod
    async def get_categories():
        categories = list(set(await ExhibitionCategory.objects()))
        categories.sort(key=lambda c: c.title, reverse=False)
        return categories

    @staticmethod
    async def format_dates(context):
        context['start_date'] = datetime.fromisoformat(str(context['start_date'])).strftime(
            '%d %B %Y at %H:%M',
        )
        context['end_date'] = datetime.fromisoformat(str(context['end_date'])).strftime(
            '%d %B %Y at %H:%M',
        )
        return context

    @staticmethod
    async def insert_format_dates(context: list):
        for elem in context:
            await ExhibitionService.format_dates(context=elem)

    @staticmethod
    async def insert_pictures(exhibition):
        return {
            **exhibition.to_dict(),
            'images': (
                exhibition.media['images']
                if isinstance(
                    exhibition.media and exhibition.media['images'],
                    str,
                )
                else exhibition.media['images']
            ),
        }

    @staticmethod
    def get_pagination_context(limit: int, offset: int, total: int):
        return {
            'limit': limit,
            'offset': offset,
            'total': total,
            'next_offset': offset + limit if offset + limit < total else None,
            'prev_offset': offset - limit if offset - limit >= 0 else None,
        }

    @staticmethod
    async def get_exhibition_by_dates(from_date: str = Query(...), until_date: str = Query(...)):
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            until_date = datetime.strptime(until_date, '%Y-%m-%d').replace(
                tzinfo=timezone.utc,
            ) + timedelta(days=1)
        except ValueError:
            raise HTTPException(status_code=400, detail='Invalid date format. Use YYYY-MM-DD')

        if from_date > until_date:
            from_date, until_date = until_date, from_date

        exhibitions = (
            await Exhibition.objects()
            .where(
                (Exhibition.start_date <= until_date) & (Exhibition.end_date >= from_date),
            )
            .prefetch(Exhibition.media, Exhibition.geo)
        )

        await ExhibitionService.insert_format_dates(context=exhibitions)

        return [await ExhibitionService.insert_pictures(e) for e in exhibitions]
