from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from piccolo.apps.user.tables import BaseUser
from piccolo_admin.endpoints import create_admin
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL

from api.apps.exhibitions.graphql.schema import schema
from api.apps.exhibitions.models import (
    Exhibition, ExhibitionCategory, ExhibitionDetails,
    ExhibitionGeo, ExhibitionTag, ExhibitionTagLink, ExhibitionContacts, ExhibitionMedia,
)
from api.apps.users.check_user import require_admin_user
from api.apps.users.models import AdminUser, Sessions
from api.apps.exhibitions.api import router as exhibition_router_api
from api.apps.exhibitions.views import router as exhibition_router_view
from api.apps.admin.api import router as admin_router_api
import logging

logger = logging.getLogger(__name__)


# ✅ Приложение
app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/docs", include_in_schema=False)
async def custom_docs(user: BaseUser = Depends(require_admin_user)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Protected Docs")

app.add_middleware(SessionMiddleware, secret_key='super-secret')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:8002'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# ✅ Admin
admin = create_admin(
    tables=[Exhibition, ExhibitionGeo, ExhibitionDetails, ExhibitionContacts, ExhibitionCategory, ExhibitionTag, ExhibitionTagLink, ExhibitionMedia, AdminUser],
    auth_table=AdminUser,
    session_table=Sessions,
)
app.mount('/admin/', admin)

# ✅ Static & Routers
app.include_router(exhibition_router_api)
app.include_router(exhibition_router_view)
app.include_router(exhibition_router_view, prefix="/categories")
app.include_router(exhibition_router_view, prefix="/exhibitions")
app.include_router(admin_router_api, prefix="/admin_api")
app.mount("/static/", StaticFiles(directory="ui/static/"), name="static")

# ✅ PubSub & GraphQL

graphql_app = GraphQLRouter(
    schema,
    subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL],
    graphiql=True,
)

app.include_router(graphql_app, prefix="/graphql")
