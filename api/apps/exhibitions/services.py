import asyncio
import logging
from datetime import datetime, timedelta, timezone

import asyncpg
from fastapi import Query
from starlette.exceptions import HTTPException
from dateutil.parser import parse

from api.apps.exhibitions.models import Exhibition, ExhibitionCategory, ExhibitionGeo
from markdown import markdown

from api.apps.exhibitions.utils import log_duration
from db import get_pool
import time

logger = logging.getLogger(__name__)

from fastapi import Depends

async def get_db_pool() -> asyncpg.pool.Pool:
    return await get_pool()

class ExhibitionService:
    def __init__(self, limit: int = 10, offset: int = 0, search: str = ''):
        self.limit = limit
        self.offset = offset
        self.search = search

    @staticmethod
    @log_duration("get_filtered")
    async def get_filtered(pool: asyncpg.pool.Pool, limit: int = 4, offset: int = 0,  search=None, countries=None, cities=None, categories=None, from_date=None, until_date=None):
        filters = []
        params = []
        idx = 1
        if search:
            filters.append(f"e.title ILIKE '%' || ${idx} || '%'")
            params.append(search)
            idx += 1

        if countries:
            filters.append(f"geo.country=ANY(${idx})")
            params.append(countries)
            idx += 1

        if cities:
            filters.append(f"geo.city=ANY(${idx})")
            params.append(cities)
            idx += 1

        if categories:
            filters.append(f"c.slug = ANY(${idx})")
            if isinstance(categories, str):
                params.append([categories])
            else:
                params.append(categories)
            idx += 1

        if from_date and until_date:
            filters.append(f"e.start_date >= ${idx} AND e.end_date <= ${idx + 1}")
            params.append(from_date)
            params.append(until_date)
            idx += 2

        where_clause = " AND ".join(filters)
        if where_clause:
            where_clause = "WHERE " + where_clause

        query = f"""
            SELECT
                e.id, e.title, e.slug, e.start_date, e.end_date, e.short_description,
                e.created_at,
                geo.location, geo.country, geo.city,
                m.images,
                c.title AS category_title, c.slug AS category_slug
            FROM exhibition e
                LEFT JOIN exhibition_geo geo ON e.geo = geo.id
                LEFT JOIN exhibition_media m ON e.media = m.id
                LEFT JOIN exhibition_category c ON e.category = c.id
            {where_clause}
            ORDER BY e.created_at DESC
            LIMIT ${idx} OFFSET ${idx + 1}
        """
        params += [limit, offset]
        count_query = f"SELECT COUNT(*) FROM exhibition e LEFT JOIN exhibition_geo geo ON e.geo = geo.id LEFT JOIN exhibition_category c ON e.category = c.id {where_clause}"
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            count = await conn.fetchval(count_query, *params[:-2])  # exclude limit/offset
        exhibitions = [dict(r) for r in rows]
        return exhibitions, count

    @staticmethod
    async def delete(slug: str):
        if not await Exhibition.select().where(Exhibition.slug == slug).first():
            raise HTTPException(status_code=404, detail='Exhibition not found')
        await Exhibition.delete().where(Exhibition.slug == slug)
        return {'message': 'Exhibition deleted', 'exhibition': slug}

    @staticmethod
    @log_duration("get_by_slug")
    async def get_by_slug(slug: str, pool: asyncpg.pool.Pool):
        async with pool.acquire() as conn:
            query = """
                SELECT 
                    e.title, e.start_date, e.end_date, 
                    c.website, c.email, c.youtube, c.linkedin, c.tiktok, c.instagram,
                    d.description,
                    m.images,
                    g.latitude, g.longitude,
                    o.name as organizer_name,
                    p.price, p.currency
                FROM exhibition e
                LEFT JOIN exhibition_contact c ON e.contact = c.id
                LEFT JOIN exhibition_detail d ON e.detail = d.id
                LEFT JOIN exhibition_media m ON e.media = m.id
                LEFT JOIN exhibition_geo g ON e.geo = g.id
                LEFT JOIN exhibition_organizer o ON e.organizer = o.id
                LEFT JOIN exhibition_price p ON e.price = p.id
                WHERE e.slug = $1
                LIMIT 1
            """
            row = await conn.fetchrow(query, slug)
        if not row:
            raise HTTPException(status_code=404, detail="Exhibition not found")
        exhibition_dict = dict(row)
        exhibition_dict['description'] = markdown(exhibition_dict['description'])
        await ExhibitionService.format_dates(context=exhibition_dict)
        return exhibition_dict

    @staticmethod
    @log_duration("get_categories")
    async def get_categories(pool: asyncpg.pool.Pool):
        async with pool.acquire() as conn:
            query = """
                SELECT DISTINCT title, slug FROM exhibition_category order by title ASC
            """
            row = await conn.fetch(query)
        categories = [{'title': r['title'], 'slug': r['slug']} for r in row]
        return categories

    @staticmethod
    @log_duration("get_countries")
    async def get_countries(pool: asyncpg.pool.Pool):
        async with pool.acquire() as conn:
            query = """
                SELECT DISTINCT country from exhibition_geo order by country ASC
            """
            rows = await conn.fetch(query)
        countries = [r["country"] for r in rows]
        return countries

    @staticmethod
    @log_duration("get_cities")
    async def get_cities(pool: asyncpg.pool.Pool):
        async with pool.acquire() as conn:
            query = """
                SELECT DISTINCT city from exhibition_geo order by city ASC
            """
            rows = await conn.fetch(query)
        cities = [r["city"] for r in rows]
        return cities

    @staticmethod
    async def format_dates(context):
        context['start_date'] = parse(str(context['start_date']))
        context['end_date'] = parse(str(context['end_date']))
        return context


    @staticmethod
    def get_pagination_context(limit: int, offset: int, total: int):
        return {
            'limit': limit,
            'offset': offset,
            'total': total,
            'next_offset': offset + limit if offset + limit < total else None,
            'prev_offset': offset - limit if offset - limit >= 0 else None,
        }
