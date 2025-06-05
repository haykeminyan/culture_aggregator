import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from piccolo.utils.sync import run_sync
from piccolo_admin.endpoints import create_admin
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL

from api.apps.admin.api import router as admin_router_api
from api.apps.exhibitions.api import router as exhibition_router_api
from api.apps.admin.views import router as custom_admin_router_api
from api.apps.exhibitions.graphql.schema import schema
from api.apps.exhibitions.models import (
    Exhibition,
    ExhibitionCategory,
    ExhibitionContact,
    ExhibitionDetail,
    ExhibitionGeo,
    ExhibitionMedia,
    ExhibitionPrice,
    ExhibitionTag,
    ExhibitionTagLink,
)
from api.apps.exhibitions.views import router as exhibition_router_view
from api.apps.users.models import AdminUser, Sessions

logger = logging.getLogger(__name__)


# ✅ Приложение
app = FastAPI(docs_url=None, redoc_url=None)


def user_is_authenticated(request):
    session_id = request.cookies.get('id')
    if not session_id:
        return False

    session = run_sync(
        Sessions.objects().where(Sessions.token == session_id).first().run(),
    )
    return session is not None and not session.has_expired


@app.get('/docs', include_in_schema=False)
async def protected_docs(request: Request):
    if not user_is_authenticated(request):
        return RedirectResponse(url='/admin/', status_code=HTTP_302_FOUND)

    return get_swagger_ui_html(openapi_url=app.openapi_url, title='Docs')


@app.get('/redoc', include_in_schema=False)
async def protected_redoc(request: Request):
    if not user_is_authenticated(request):
        return RedirectResponse(url='/admin/', status_code=HTTP_302_FOUND)

    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
          <head>
            <title>ReDoc</title>
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
          </head>
          <body>
            <redoc spec-url="{app.openapi_url}"></redoc>
            <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
          </body>
        </html>
        """,
    )


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
    tables=[
        Exhibition,
        ExhibitionGeo,
        ExhibitionDetail,
        ExhibitionContact,
        ExhibitionCategory,
        ExhibitionPrice,
        ExhibitionTag,
        ExhibitionTagLink,
        ExhibitionMedia,
        AdminUser,
    ],
    auth_table=AdminUser,
    session_table=Sessions,
)
app.mount('/admin/', admin)
app.include_router(exhibition_router_api)

# ✅ Static & Routers
app.include_router(custom_admin_router_api)
app.include_router(exhibition_router_view)
app.include_router(exhibition_router_view, prefix='/categories')
app.include_router(exhibition_router_view, prefix='/exhibitions')
app.include_router(admin_router_api, prefix='/admin_api')
app.mount('/static/', StaticFiles(directory='ui/static/'), name='static')

# ✅ PubSub & GraphQL

graphql_app = GraphQLRouter(
    schema,
    subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL],
    graphiql=True,
)

app.include_router(graphql_app, prefix='/graphql')
