# admin/routes.py
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import pytz
from fastapi import APIRouter, File, Form, Request, UploadFile, Query
from piccolo.query import Select
from sqlalchemy.testing.util import total_size
from starlette.responses import RedirectResponse

from api.apps.admin.services import AdminService
from api.apps.exhibitions.models import Exhibition
from api.core.templates import templates
from piccolo.query.functions import Count

logger = logging.getLogger(__name__)


UPLOAD_DIR = 'ui/static/exhibitions/exhibition_pictures'

os.makedirs(UPLOAD_DIR, exist_ok=True)
router = APIRouter(prefix='/custom_admin')


@router.get('/exhibitions/')
async def exhibition_list(request: Request,     limit: int = Query(4),
    offset: int = Query(0),
                          search: Optional[str] = Query(''),):

    query: Select = Exhibition.select().order_by(Exhibition.created_at)
    if search:
        query = query.where(Exhibition.title.ilike(f'%{search}%'))

    # Count query (must NOT select non-aggregated fields)
    count_query = Exhibition.select(Count(alias='total'))
    if search:
        count_query = count_query.where(Exhibition.title.ilike(f'%{search}%'))

    total_row = await count_query.first()
    total = total_row['total'] if total_row else 0

    # Get paginated results
    paginated_exhibitions = await query.limit(limit).offset(offset)

    return templates.TemplateResponse(
        'admin/exhibition_list.html',
        {
            'request': request,
            'exhibitions': paginated_exhibitions,
            'limit': limit,
            'offset': offset,
            'total': total,
            'search': search,
            **AdminService.get_pagination_context(limit, offset, total),
            'now': datetime.now(pytz.UTC),
        },
    )


@router.get('/exhibition/create/')
async def exhibition_form_create(request: Request):
    exhibition = await Exhibition.objects().prefetch(
        Exhibition.category,
    )
    return templates.TemplateResponse(
        'admin/exhibition_create.html',
        {
            'request': request,
            'exhibition': exhibition,
            'now': datetime.now(pytz.UTC),
            'tomorrow': datetime.now(pytz.UTC) + timedelta(days=7),
        },
    )


@router.post('/exhibition/create/')
async def exhibition_create(
    title: str = Form(default='title'),
    slug: str = Form(default='slug'),
    images: Optional[list[UploadFile]] = File(default=None, include_in_schema=False),
    short_description: str = Form(default='Very short description'),
    category_title: str = Form(default='category title'),
    category_slug: str = Form(default='category slug'),
    start_date: datetime = Form(default=datetime.now(pytz.UTC)),
    end_date: datetime = Form(default=datetime.now(pytz.UTC)),
    detail: str = Form(default='full information about exhibition'),
    location: str = Form(default='Location'),
    latitude: float = Form(default=40.1814),
    longitude: float = Form(default=44.5144),
    country: str = Form(default='Armenia'),
    city: str = Form(default='Yerevan'),
    price: str = Form(default='price'),
    currency: str = Form(default='AMD'),
    organizer_name: str = Form(default='AshotOrganizer'),
    website: str = Form(default='https://baregorc.com'),
    youtube: str = Form(default='https://www.youtube.com'),
    instagram: str = Form(default='https://www.instagram.com'),
    linkedin: str = Form(default='https://www.linkedin.com'),
    tiktok: str = Form(default='https://www.tiktok.com'),
):
    await AdminService.create_exhibition(
        title,
        slug,
        images,
        short_description,
        category_title,
        category_slug,
        start_date,
        end_date,
        detail,
        location,
        latitude,
        longitude,
        country,
        city,
        price,
        currency,
        organizer_name,
        website,
        youtube,
        instagram,
        linkedin,
        tiktok,
    )
    return RedirectResponse('/custom_admin/exhibitions/', status_code=303)


@router.get('/exhibition/{exhibition_slug}/')
async def exhibition_form(request: Request, exhibition_slug: str):
    exhibition = (
        await Exhibition.objects()
        .where(Exhibition.slug == exhibition_slug)
        .prefetch(
            Exhibition.category,
            Exhibition.geo,
            Exhibition.detail,
            Exhibition.contact,
            Exhibition.media,
            Exhibition.price,
            Exhibition.organizer,
        )
        .first()
    )
    return templates.TemplateResponse(
        'admin/exhibition_update.html',
        {
            'request': request,
            'exhibition': exhibition,
        },
    )


@router.post('/exhibition/{exhibition_slug}/')
async def exhibition_update(
    slug: str = Form(default='title'),
    title: str = Form(default='title'),
    images: Optional[list[UploadFile]] = File(default=None, include_in_schema=False),
    remaining_images: Optional[str] = Form(default=None),
    short_description: str = Form(default='Very short description'),
    category_title: str = Form(default='category title'),
    category_slug: str = Form(default='category slug'),
    start_date: datetime = Form(default=datetime.now(pytz.UTC)),
    end_date: datetime = Form(default=datetime.now(pytz.UTC)),
    detail: str = Form(default='full information about exhibition'),
    location: str = Form(default='Location'),
    latitude: float = Form(default=40.1814),
    longitude: float = Form(default=44.5144),
    country: str = Form(default='Armenia'),
    city: str = Form(default='Yerevan'),
    price: str = Form(default='price'),
    currency: str = Form(default='AMD'),
    organizer_name: str = Form(default='AshotOrganizer'),
    website: str = Form(default='https://baregorc.com'),
    youtube: str = Form(default='https://www.youtube.com'),
    instagram: str = Form(default='https://www.instagram.com'),
    linkedin: str = Form(default='https://www.linkedin.com'),
    tiktok: str = Form(default='https://www.tiktok.com'),
):
    await AdminService.update_exhibition(
        slug,
        title,
        images,
        remaining_images,
        short_description,
        category_title,
        category_slug,
        start_date,
        end_date,
        detail,
        location,
        latitude,
        longitude,
        country,
        city,
        price,
        currency,
        organizer_name,
        website,
        youtube,
        instagram,
        linkedin,
        tiktok,
    )
    return RedirectResponse('/custom_admin/exhibitions/', status_code=303)


@router.post('/exhibition/{exhibition_slug}/delete/')
async def exhibition_delete(
    exhibition_slug: str,
):
    await AdminService.delete_exhibition(exhibition_slug)
    return RedirectResponse('/custom_admin/exhibitions/', status_code=303)
