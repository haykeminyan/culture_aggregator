# routes/admin/exhibitions.py
from fastapi import HTTPException
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from api.apps.admin.services import AdminService
from api.apps.exhibitions.models import Exhibition, ExhibitionDetail, ExhibitionGeo, ExhibitionMedia, \
    ExhibitionContact, ExhibitionCategory

import os

import logging

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = "ui/static/exhibitions/exhibition_pictures"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/exhibitions/create/", response_class=HTMLResponse)
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
    website: str = Form(default='https://baregorc.com'),
    youtube: str = Form(default='https://www.youtube.com'),
    instagram: str = Form(default='https://www.instagram.com'),
    linkedin: str = Form(default='https://www.linkedin.com'),
    tiktok: str = Form(default='https://www.tiktok.com'),
):

    if " " in slug:
        return JSONResponse({"error": "Slug cannot contain spaces."}, status_code=400)

    # check if exhibition is already created
    exists = await Exhibition.exists().where(Exhibition.slug == slug)
    if exists:
        return JSONResponse({"error": "Exhibition with this slug already exists."}, status_code=400)

    category = await AdminService().check_unique_category_title_slug(category_title, category_slug)

    detail = await ExhibitionDetail.objects().create(description=detail)
    geo = await ExhibitionGeo.objects().create(location=location, city=city, country=country, latitude=latitude, longitude=longitude)
    contact = await ExhibitionContact.objects().create(website=website, youtube=youtube, instagram=instagram, linkedin=linkedin, tiktok=tiktok)

    # Сохраняем изображения и формируем список путей
    saved_paths = []

    # 1. Обработка загруженных изображений
    if images:
        for image in images:
            try:
                filename = os.path.join(UPLOAD_DIR, image.filename)
                with open(filename, "wb") as buffer:
                    buffer.write(await image.read())
                relative_path = os.path.relpath(filename, "ui/static")
                saved_paths.append(relative_path)
            except AttributeError:
                pass

    # 2. Если нет изображений — используем дефолтное
    if not saved_paths:
        saved_paths = ["exhibitions/exhibition_pictures/default_image.png"]

    # 3. Проверяем, существует ли такая же запись
    media = await ExhibitionMedia.objects().where(
        ExhibitionMedia.images == saved_paths
    ).first()

    # 4. Если нет — создаём новую
    if not media:
        media = await ExhibitionMedia.objects().create(images=saved_paths)

    # ✅ Теперь создаём выставку и привязываем media
    await Exhibition.objects().create(
        title=title,
        slug=slug,
        short_description=short_description,
        category=category['id'],
        detail=detail["id"],
        geo=geo["id"],
        contact=contact["id"],
        media=media["id"],
    )

    return HTMLResponse(f"<div class='text-green-600'>Exhibition {title} created successfully!</div>")



@router.put("/exhibitions/{exhibition_slug}/", response_class=HTMLResponse)
async def update_exhibition(
    exhibition_slug: str,
    title: str = Form(...),
    images: Optional[list[UploadFile]] = File(default=None, include_in_schema=False),
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
    exhibition = await Exhibition.objects().where(Exhibition.slug == exhibition_slug).first()
    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")

    exhibition.title = title
    exhibition.short_description = short_description

    # update categories fields
    category = await ExhibitionCategory.objects().where(ExhibitionCategory.slug == category_slug).first()
    if category:
        exhibition.category = category["id"]
    else:
        new_category = await ExhibitionCategory.objects().create(
            title=category_title,
            slug=category_slug
        )
        exhibition.category = new_category["id"]


    # update contacts fields
    geo = await ExhibitionGeo.objects().get(ExhibitionGeo.id == exhibition.geo)
    geo.location = location
    geo.latitude = latitude
    geo.longitude = longitude
    geo.country = country
    geo.city = city
    await geo.save()

    # update geo fields
    contacts = await ExhibitionContact.objects().get(ExhibitionContact.id == exhibition.contacts)
    contacts.website = website
    contacts.youtube = youtube
    contacts.instagram = instagram
    contacts.linkedin = linkedin
    contacts.tiktok = tiktok
    await contacts.save()

    # update images
    media = await ExhibitionMedia.objects().get(ExhibitionMedia.id == exhibition.media)
    if images:
        saved_paths = []
        for image in images:
            filename = os.path.join(UPLOAD_DIR, image.filename)
            with open(filename, "wb") as buffer:
                buffer.write(await image.read())
            relative_path = os.path.relpath(filename, "ui/static")
            saved_paths.append(relative_path)

        if media:
            media.images = saved_paths
            await media.save()
        else:
            new_media = await ExhibitionMedia.objects().create(images=saved_paths)
            exhibition.media = new_media["id"]

    # update details fields
    details_obj = await ExhibitionDetail.objects().get(ExhibitionDetail.id == exhibition.details)
    details_obj.description = details
    await details_obj.save()

    await exhibition.save()

    return HTMLResponse(f"<div class='text-green-600'>Exhibition {exhibition_slug} updated successfully!</div>")