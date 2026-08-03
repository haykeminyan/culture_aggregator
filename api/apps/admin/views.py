# admin/routes.py
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from piccolo.utils.sync import run_sync

from api.apps.users.models import AdminUser, Sessions
from piccolo_api.session_auth.endpoints import session_logout


import pytz
from fastapi import APIRouter, File, Form, Request, UploadFile, Query, Depends
from piccolo.query import Select
from starlette import status
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

from api.apps.admin.services import AdminService
from api.apps.exhibitions.models import Exhibition
from api.core.templates import templates
from piccolo.query.functions import Count

from auth_utils import auth_dependency_router

logger = logging.getLogger(__name__)


UPLOAD_DIR = 'ui/static/exhibitions/exhibition_pictures'

os.makedirs(UPLOAD_DIR, exist_ok=True)
router = APIRouter(prefix='/custom_admin', dependencies=[Depends(auth_dependency_router)])



@router.get('/', include_in_schema=False)
async def admin_index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='admin/index.html',
        context={
            'request': request,
            'now': datetime.now(pytz.UTC),
        }
    )

@router.get('/logout/')
async def logout(request: Request):
    session_id = request.cookies.get('id')
    if session_id:
        await Sessions.delete().where(Sessions.token == session_id).run()

    response = RedirectResponse(url='/admin/', status_code=302)
    response.delete_cookie('id')
    return response



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
        request=request,
        name='admin/exhibition_list.html',
        context={
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
        request=request,
        name='admin/exhibition_create.html',
        context={
            'request': request,
            'exhibition': exhibition,
            'now': datetime.now(pytz.UTC),
            'tomorrow': datetime.now(pytz.UTC) + timedelta(days=7),
        },
    )


@router.post('/exhibition/create/')
async def exhibition_create(
request: Request,
    title: str = Form(),
    slug: str = Form(),
    images: Optional[list[UploadFile]] = File(default=None, include_in_schema=False),
    short_description: str = Form(),
    category_title: str = Form(),
    category_slug: str = Form(),
    start_date: datetime = Form(default=datetime.now(pytz.UTC)),
    end_date: datetime = Form(default=datetime.now(pytz.UTC)),
    detail: str = Form(),
    location: str = Form(),
        email: str = Form(),
    latitude: float = Form(),
    longitude: float = Form(),
    country: str = Form(),
    city: str = Form(),
    price: str = Form(),
    currency: str = Form(),
    organizer_name: str = Form(),
    website: str = Form(),
    youtube: str = Form(),
    instagram: str = Form(),
    linkedin: str = Form(),
    tiktok: str = Form(),
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
        email,
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
        request=request,
        name='admin/exhibition_update.html',
        context={
            'request': request,
            'exhibition': exhibition,
        },
    )


@router.post('/exhibition/{exhibition_slug}/')
async def exhibition_update(
    slug: str = Form(),
    title: str = Form(),
    images: Optional[list[UploadFile]] = File(default=None, include_in_schema=False),
    remaining_images: Optional[str] = Form(default=None),
    short_description: str = Form(),
    category_title: str = Form(),
    category_slug: str = Form(),
    start_date: datetime = Form(),
    end_date: datetime = Form(),
    detail: str = Form(),
    location: str = Form(),
    latitude: float = Form(),
    longitude: float = Form(),
    country: str = Form(),
    city: str = Form(),
    price: str = Form(),
    currency: str = Form(),
    organizer_name: str = Form(),
    website: str = Form(),
    youtube: str = Form(),
    instagram: str = Form(),
    linkedin: str = Form(),
    tiktok: str = Form(),
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




