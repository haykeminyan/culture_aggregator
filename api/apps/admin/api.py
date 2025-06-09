# routes/admin/exhibitions.py
import logging
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import HTMLResponse

from api.apps.admin.services import AdminService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/exhibitions/create/', response_class=HTMLResponse)
async def create_exhibition(
    title: str = Form(default='title'),
    slug: str = Form(default='slug'),
    images: Optional[list[UploadFile]] = File(default=None, include_in_schema=False),
    short_description: str = Form(default='Very short description'),
    category_title: str = Form(default='category title'),
    category_slug: str = Form(default='category slug'),
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

    return await AdminService.create_exhibition(
        title,
        slug,
        images,
        short_description,
        category_title,
        category_slug,
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


@router.put('/exhibitions/{exhibition_slug}/', response_class=HTMLResponse)
async def update_exhibition(
    exhibition_slug: str,
    title: str = Form(...),
    images: Optional[list[UploadFile]] = File(default=None, include_in_schema=False),
    remaining_images: Optional[str] = Form(default=None),
    short_description: str = Form(...),
    category_title: str = Form(...),
    category_slug: str = Form(...),
    details: str = Form(...),
    location: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    country: str = Form(...),
    city: str = Form(...),
    website: str = Form(...),
    youtube: str = Form(...),
    instagram: str = Form(...),
    linkedin: str = Form(...),
    tiktok: str = Form(...),
):
    return await AdminService.update_exhibition(
        exhibition_slug,
        title,
        images,
        remaining_images,
        short_description,
        category_title,
        category_slug,
        details,
        location,
        latitude,
        longitude,
        country,
        city,
        website,
        youtube,
        instagram,
        linkedin,
        tiktok,
    )
