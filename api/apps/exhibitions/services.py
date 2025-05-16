from starlette.exceptions import HTTPException
from fastapi import Query

from api.apps.exhibitions.models import Exhibition, ExhibitionGeo, ExhibitionCategory, ExhibitionDetails, \
    ExhibitionTagLink
from api.apps.exhibitions.schemas import ExhibitionCreate
import logging
from api.apps.exhibitions.utils import slugify

logger = logging.getLogger(__name__)

async def create_exhibition(data: ExhibitionCreate):
    geo = await ExhibitionGeo.objects().create(
        location=data.geo.location,
        latitude=data.geo.latitude,
        longitude=data.geo.longitude,
        country=data.geo.country,
        city=data.geo.city,
    )
    slug = await Exhibition.select().where(Exhibition.slug == data.slug).first()
    if slug:
        raise HTTPException(status_code=400, detail="Exhibition is already created")

    category_slug = data.category.slug or slugify(data.category.title)
    category = await ExhibitionCategory.select().where(ExhibitionCategory.slug == category_slug).first()
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
    return {"message": "Exhibition created", "exhibition": exhibition.to_dict()}


async def delete_exhibition(slug: str):
    existing = await Exhibition.select().where(Exhibition.slug == slug).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    else:
        await Exhibition.delete().where(Exhibition.slug == slug)
    return {"message": "Exhibition deleted", "exhibition": slug}


async def get_exhibition(slug: str):
    exhibition = await Exhibition.select().where(Exhibition.slug == slug).first()
    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    return exhibition

async def get_all_exhibitions_by_category( category_slug: str):
    category = await ExhibitionCategory.select().where(
        ExhibitionCategory.slug == category_slug
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    exhibitions = await Exhibition.select().where(Exhibition.category == category['id']).order_by(Exhibition.created_at, ascending=False)
    if not exhibitions:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    return exhibitions

async def get_all_exhibitions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
)-> dict:
    total = await Exhibition.count()
    exhibitions = await Exhibition.objects().limit(limit).offset(offset).order_by(Exhibition.created_at, ascending=False)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [e.to_dict() for e in exhibitions]
    }
