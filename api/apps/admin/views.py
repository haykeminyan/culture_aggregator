# admin/routes.py

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from api.apps.exhibitions.models import Exhibition
from api.core.templates import templates

router = APIRouter(prefix="/custom_admin")

@router.get("/exhibitions/")
async def exhibition_list(request: Request):
    exhibitions = await Exhibition.select().order_by(Exhibition.created_at)
    return templates.TemplateResponse("admin/exhibition_list.html", {
        "request": request,
        "exhibitions": exhibitions
    })

@router.get("/exhibitions/create/")
async def exhibition_form(request: Request):
    from api.apps.exhibitions.models import ExhibitionCategory
    categories = await ExhibitionCategory.select()
    return templates.TemplateResponse("admin/exhibition_form.html", {
        "request": request,
        "categories": categories,
    })