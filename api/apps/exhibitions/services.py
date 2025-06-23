import logging
from datetime import datetime, timedelta, timezone

from fastapi import Query
from starlette.exceptions import HTTPException
from dateutil.parser import parse

from api.apps.exhibitions.models import Exhibition, ExhibitionCategory, ExhibitionGeo
from markdown import markdown

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
        )
        if filter_:
            query = query.where(filter_)
        query = query.prefetch(
                Exhibition.geo,
                Exhibition.category,
                Exhibition.detail,
                Exhibition.contact,
                Exhibition.media)
        exhibitions = await query.offset(self.offset).limit(self.limit).order_by('-created_at').all()

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
    async def get_filtered(countries=None, cities=None, categories=None, from_date=None, until_date=None):
        query = Exhibition.objects().prefetch(
            Exhibition.media,
            Exhibition.category,
            Exhibition.geo,
        )

        if countries and cities:
            geo_ids = await ExhibitionGeo.select(ExhibitionGeo.id).where(
                ExhibitionGeo.country.is_in(countries),
                ExhibitionGeo.city.is_in(cities),
            ).run()
            geo_ids = [g['id'] for g in geo_ids]
            query = query.where(Exhibition.geo.is_in(geo_ids))
        elif countries:
            geo_ids = await ExhibitionGeo.select(ExhibitionGeo.id).where(
                ExhibitionGeo.country.is_in(countries)
            ).run()
            geo_ids = [g['id'] for g in geo_ids]
            query = query.where(Exhibition.geo.is_in(geo_ids))
        elif cities:
            geo_ids = await ExhibitionGeo.select(ExhibitionGeo.id).where(
                ExhibitionGeo.city.is_in(cities)
            ).run()
            geo_ids = [g['id'] for g in geo_ids]
            query = query.where(Exhibition.geo.is_in(geo_ids))

        if categories:
            category_objs = await ExhibitionService.get_by_category(categories)
            logger.error(category_objs)
            category_ids = [c['id'] for c in category_objs]
            query = query.where(Exhibition.category.is_in(category_ids))

        # Фильтрация по датам
        if from_date and until_date:
            query = query.where(
                (Exhibition.start_date >= from_date) &
                (Exhibition.end_date <= until_date)
            )

        results = await query.run()
        await ExhibitionService.insert_format_dates(results)
        return [await ExhibitionService.insert_pictures(e) for e in results]

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
                Exhibition.detail,
                Exhibition.media,
                Exhibition.geo,
                Exhibition.organizer,
                Exhibition.price,
            )
            .first()
        )
        exhibition.detail = markdown(exhibition.detail.to_dict()['description'])
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
    async def get_by_country(country: str):
        country = (
            await ExhibitionGeo.objects()
            .where(ExhibitionGeo.country == country)
        )
        country_ids = [geo['id'] for geo in country]

        exhibitions = (
            await Exhibition.objects()
            .where(Exhibition.geo.is_in(country_ids))
            .prefetch(Exhibition.media, Exhibition.category, Exhibition.geo)
        )
        await ExhibitionService.insert_format_dates(context=exhibitions)

        return [await ExhibitionService.insert_pictures(e) for e in exhibitions]

    @staticmethod
    async def get_countries():
        countries = await ExhibitionGeo.objects()
        country_unique = []
        for elem in countries:
            if elem.country not in country_unique:
                country_unique.append(elem.country)
        return sorted(country_unique)

    @staticmethod
    async def get_by_city(city: str):
        city = (
            await ExhibitionGeo.objects()
            .where(ExhibitionGeo.city == city)
        )
        city_ids = [geo['id'] for geo in city]

        exhibitions = (
            await Exhibition.objects()
            .where(Exhibition.geo.is_in(city_ids))
            .prefetch(Exhibition.media, Exhibition.category, Exhibition.geo)
        )
        await ExhibitionService.insert_format_dates(context=exhibitions)

        return [await ExhibitionService.insert_pictures(e) for e in exhibitions]

    @staticmethod
    async def get_cities():
        cities = await ExhibitionGeo.objects()
        city_unique = []
        for elem in cities:
            if elem.city not in city_unique:
                city_unique.append(elem.city)
        return sorted(city_unique)

    @staticmethod
    async def format_dates(context):
        context['start_date'] = parse(str(context['start_date']))
        context['end_date'] = parse(str(context['end_date']))
        return context

    @staticmethod
    async def insert_format_dates(context: list):
        for elem in context:
            await ExhibitionService.format_dates(context=elem)

    @staticmethod
    async def insert_pictures(exhibition):
        if isinstance(exhibition, dict):
            exhibition_dict = exhibition
        else:
            exhibition_dict = exhibition.to_dict()

        return {
            **exhibition_dict,
            'images': (
                exhibition['media']['images']
                if isinstance(
                    exhibition['media'] and exhibition['media']['images'],
                    str,
                )
                else exhibition['media']['images']
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
