# routes/admin/exhibitions.py
from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from piccolo.columns import DoublePrecision
from starlette.responses import JSONResponse
from piccolo.utils.sync import run_sync
from api.apps.exhibitions.models import Exhibition, ExhibitionCategory, ExhibitionDetails, ExhibitionGeo, ExhibitionMedia

import os

from api.apps.exhibitions.utils import slugify
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = "ui/static/exhibitions/exhibition_pictures"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/adminka/exhibitions/create/", response_class=HTMLResponse)
async def create_exhibition(
    title: str = Form(...),
    slug: str = Form(...),
    short_description: str = Form(...),
    category_title: str = Form(...),
    category_slug: str = Form(...),
    details: str = Form(...),
    location: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    country: str = Form(...),
    city: str = Form(...),
    images: list[UploadFile] = File(...),
):

    if " " in slug:
        return JSONResponse({"error": "Slug cannot contain spaces."}, status_code=400)

    # check if exhibition is already created
    exists = await Exhibition.exists().where(Exhibition.slug == slug)
    if exists:
        return JSONResponse({"error": "Exhibition with this slug already exists."}, status_code=400)

    existing_title = await ExhibitionCategory.select().where(ExhibitionCategory.title == category_title).first()
    existing_slug = await ExhibitionCategory.select().where(ExhibitionCategory.slug == category_slug).first()

    if existing_title and existing_slug:
        if existing_title['id'] == existing_slug['id']:
            category = existing_title
        else:
            return JSONResponse(
                {"error": "This title belongs to a different category than this slug."},
                status_code=400
            )
    elif existing_title:
        return JSONResponse(
            {"error": "Category with this title already exists with another slug."},
            status_code=400
        )

    elif existing_slug:
        return JSONResponse(
            {"error": "Category with this slug already exists with another title."},
            status_code=400
        )
    else:
        category = await ExhibitionCategory.objects().create(title=category_title, slug=category_slug)

    details = await ExhibitionDetails.objects().create(description=details)
    geo = await ExhibitionGeo.objects().create(location=location, city=city, country=country, latitude=latitude, longitude=longitude)

    # Сохраняем изображения и формируем список путей
    saved_paths = []
    for image in images:
        filename = os.path.join(UPLOAD_DIR, image.filename)
        with open(filename, "wb") as buffer:
            buffer.write(await image.read())
        relative_path = os.path.relpath(filename, "ui/static")
        saved_paths.append(relative_path)

    # ✅ Создаём медиа
    media = await ExhibitionMedia.objects().create(images=saved_paths)

    # ✅ Теперь создаём выставку и привязываем media
    await Exhibition.objects().create(
        title=title,
        slug=slug,
        short_description=short_description,
        category=category['id'],
        details=details["id"],
        geo=geo["id"],
        media=media["id"],
    )

    return HTMLResponse("<div class='text-green-600'>Exhibition created successfully!</div>")
