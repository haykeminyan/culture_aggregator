# routes/admin/exhibitions.py
import json
import logging
import os
import uuid

from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from api.apps.admin.schemas import CategoryDict
from api.apps.exhibitions.models import (
    Exhibition,
    ExhibitionCategory,
    ExhibitionContact,
    ExhibitionDetail,
    ExhibitionGeo,
    ExhibitionMedia,
    ExhibitionOrganizer,
    ExhibitionPrice,
)

logger = logging.getLogger(__name__)

UPLOAD_DIR = 'ui/static/exhibitions/exhibition_pictures'

os.makedirs(UPLOAD_DIR, exist_ok=True)


class AdminService:
    @staticmethod
    async def check_unique_category_title_slug(title: str, slug: str) -> CategoryDict:
        existing_title = (
            await ExhibitionCategory.select().where(ExhibitionCategory.title == title).first()
        )
        existing_slug = (
            await ExhibitionCategory.select().where(ExhibitionCategory.slug == slug).first()
        )
        if existing_title and existing_slug:
            if existing_title['id'] == existing_slug['id']:
                category = existing_title
            else:
                raise HTTPException(
                    status_code=400,
                    detail='This title belongs to a different category than this slug.',
                )
        elif existing_title:
            raise HTTPException(
                status_code=400,
                detail='Category with this title already exists with another slug.',
            )

        elif existing_slug:
            raise HTTPException(
                status_code=400,
                detail='Category with this slug already exists with another title.',
            )
        else:
            category = await ExhibitionCategory.objects().create(title=title, slug=slug)
        return category

    @staticmethod
    async def create_exhibition(
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
    ):
        if ' ' in slug:
            return JSONResponse({'error': 'Slug cannot contain spaces.'}, status_code=400)

        # check if exhibition is already created
        exists = await Exhibition.exists().where(Exhibition.slug == slug)
        if exists:
            return JSONResponse(
                {'error': 'Exhibition with this slug already exists.'},
                status_code=400,
            )

        category = await AdminService().check_unique_category_title_slug(
            category_title,
            category_slug,
        )

        detail = await ExhibitionDetail.objects().create(description=detail)
        geo = await ExhibitionGeo.objects().create(
            location=location,
            city=city,
            country=country,
            latitude=latitude,
            longitude=longitude,
        )
        contact = await ExhibitionContact.objects().create(
            website=website,
            youtube=youtube,
            instagram=instagram,
            linkedin=linkedin,
            tiktok=tiktok,
        )

        price = await ExhibitionPrice.objects().create(
            price=price,
            currency=currency,
        )

        organizer = await ExhibitionOrganizer.objects().create(
            name=organizer_name,
        )

        # Сохраняем изображения и формируем список путей
        saved_paths = []

        # 1. Обработка загруженных изображений
        if images:
            for image in images:
                try:
                    filename = os.path.join(UPLOAD_DIR, image.filename)
                    with open(filename, 'wb') as buffer:
                        buffer.write(await image.read())
                    relative_path = os.path.relpath(filename, 'ui/static')
                    saved_paths.append(relative_path)
                except AttributeError:
                    pass

        # 2. Если нет изображений — используем дефолтное
        if not saved_paths:
            saved_paths = ['exhibitions/exhibition_pictures/default_image.png']

        # 3. Проверяем, существует ли такая же запись
        media = (
            await ExhibitionMedia.objects()
            .where(
                ExhibitionMedia.images == saved_paths,
            )
            .first()
        )

        # 4. Если нет — создаём новую
        if not media:
            media = await ExhibitionMedia.objects().create(images=saved_paths)

        # ✅ Теперь создаём выставку и привязываем media
        await Exhibition.objects().create(
            title=title,
            slug=slug,
            start_date=start_date,
            end_date=end_date,
            short_description=short_description,
            category=category['id'],
            detail=detail['id'],
            geo=geo['id'],
            contact=contact['id'],
            price=price['id'],
            organizer=organizer['id'],
            media=media['id'],
        )

        return HTMLResponse(
            f"<div class='text-green-600'>Exhibition {title} created successfully!</div>",
        )

    @staticmethod
    async def update_exhibition(
        exhibition_slug,
        title,
        images,
        remaining_images,
        short_description,
        category_title,
        category_slug,
        start_date,
        end_date,
        details,
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
    ):
        exhibition = await Exhibition.objects().where(Exhibition.slug == exhibition_slug).first()
        if not exhibition:
            raise HTTPException(status_code=404, detail='Exhibition not found')

        exhibition.title = title
        exhibition.short_description = short_description
        exhibition.start_date = start_date
        exhibition.end_date = end_date

        category = (
            await ExhibitionCategory.objects()
            .where(ExhibitionCategory.slug == category_slug)
            .first()
        )
        if category:
            exhibition.category = category['id']
        else:
            new_category = await ExhibitionCategory.objects().create(
                title=category_title,
                slug=category_slug,
            )
            exhibition.category = new_category['id']

        # update contacts fields
        geo = await ExhibitionGeo.objects().get(ExhibitionGeo.id == exhibition.geo)
        if geo:
            geo.location = location
            geo.latitude = latitude
            geo.longitude = longitude
            geo.country = country
            geo.city = city
            await geo.save()

        # update geo fields
        contacts = await ExhibitionContact.objects().get(
            ExhibitionContact.id == exhibition.contact,
        )
        if contacts:
            contacts.website = website
            contacts.youtube = youtube
            contacts.instagram = instagram
            contacts.linkedin = linkedin
            contacts.tiktok = tiktok
            await contacts.save()

        organizer = await ExhibitionOrganizer.objects().get(
            ExhibitionOrganizer.id == exhibition.organizer,
        )
        if organizer:
            organizer.name = organizer_name
            await organizer.save()

        prices = await ExhibitionPrice.objects().get(ExhibitionPrice.id == exhibition.price)
        if prices:
            prices.price = price
            prices.currency = currency
            await prices.save()

        # update images
        media = await ExhibitionMedia.objects().get(ExhibitionMedia.id == exhibition.media)

        if media:
            current_images = media.images or []

            if remaining_images:
                if isinstance(remaining_images, str):
                    remaining_images = json.loads(remaining_images)
            else:
                remaining_images = []

        # Then append new images if any:
            images_to_delete = set(current_images) - set(remaining_images)
            for rel_path in images_to_delete:
                abs_path = os.path.join('ui/static', rel_path)
                if os.path.exists(abs_path):
                    os.remove(abs_path)

            # Update with only remaining images
            media.images = remaining_images
            await media.save()

        # Then append new images if any:
        if images:
            saved_paths = []
            for image in images:
                if not image.filename or image.filename.endswith('/'):
                    continue
                safe_filename = os.path.basename(image.filename)
                ext = os.path.splitext(safe_filename)[1]
                unique_name = f'{uuid.uuid4().hex}{ext}'
                filepath = os.path.join(UPLOAD_DIR, unique_name)
                with open(filepath, 'wb') as buffer:
                    buffer.write(await image.read())
                relative_path = os.path.relpath(filepath, 'ui/static')
                saved_paths.append(relative_path)

            if media:
                media.images.extend(saved_paths)
                await media.save()
            else:
                new_media = await ExhibitionMedia.objects().create(images=saved_paths)
                exhibition.media = new_media['id']

        # update details fields
        details_obj = await ExhibitionDetail.objects().get(
            ExhibitionDetail.id == exhibition.detail,
        )
        if details_obj:
            details_obj.description = details
            await details_obj.save()

        await exhibition.save()

        return HTMLResponse(
            f"<div class='text-green-600'>Exhibition {exhibition_slug} updated successfully!</div>",
        )

    @staticmethod
    async def delete_exhibition(slug: str):
        return await Exhibition.delete().where(Exhibition.slug == slug)
