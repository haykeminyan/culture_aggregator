from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from piccolo_admin.endpoints import create_admin
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from api.apps.exhibitions.api import router as exhibition_router_api
from api.apps.exhibitions.models import (
    Exhibition,
    ExhibitionCategory,
    ExhibitionDetails,
    ExhibitionGeo,
    ExhibitionTag,
    ExhibitionTagLink,
)
from api.apps.exhibitions.views import router as exhibition_router_view
from api.apps.users.models import AdminUser, Sessions

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='super-secret')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:8002'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
# 🔐 Session middleware для CSRF и логина

# 🛠 Подключаем админку
admin = create_admin(
    tables=[
        Exhibition,
        ExhibitionGeo,
        ExhibitionDetails,
        ExhibitionCategory,
        ExhibitionTag,
        ExhibitionTagLink,
        AdminUser,
    ],
    auth_table=AdminUser,
    session_table=Sessions,
)

app.mount('/admin/', admin)
app.include_router(exhibition_router_api)
app.include_router(exhibition_router_view)
app.mount("/ui/", StaticFiles(directory="ui/static/css/"), name="static")
