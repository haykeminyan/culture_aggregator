import logging
import os
import socket
from datetime import datetime

import asyncpg
import pytz
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from piccolo.utils.sync import run_sync
from piccolo_admin.endpoints import create_admin
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL
from dotenv import load_dotenv

# Routers and models
from api.apps.admin.api import router as admin_router_api
from api.apps.admin.views import router as custom_admin_router_api
from api.apps.exhibitions.api import router as exhibition_router_api
from api.apps.exhibitions.views import router as exhibition_router_view
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
from api.apps.users.models import AdminUser, Sessions
from contextlib import asynccontextmanager

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    raw_dsn = os.getenv("DATABASE_URL")
    if not raw_dsn:
        raise RuntimeError("DATABASE_URL environment variable not set")

    asyncpg_dsn = raw_dsn.replace("+asyncpg", "")

    # Try resolving the host before pool creation to catch issues early
    try:
        host = asyncpg_dsn.split("@")[1].split("/")[0].split(":")[0]
        socket.gethostbyname(host)
    except Exception as e:
        print(f"Cannot resolve host '{host}': {e}")
        raise  # optionally re-raise to fail startup

    app.state.pool = await asyncpg.create_pool(dsn=asyncpg_dsn)
    try:
        yield
    finally:
        await app.state.pool.close()


# App
# app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)
app = FastAPI(docs_url=None, redoc_url=None)

# -------------------- Config --------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret")
ALLOWED_ORIGINS = [
    'http://127.0.0.1:8002',
    'http://localhost:8002',
    'https://travelculturehub.com',
    'https://www.travelculturehub.com',
    'https://travelculture.baregorc.com',
    'https://www.travelculture.baregorc.com'
]
STATIC_DIR = "/app/ui/static"
# ------------------------------------------------


# ------------------ Middleware ------------------

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")
        logger.info(f"Origin: {origin}, Referer: {referer}")
        response = await call_next(request)
        return response

app.add_middleware(LoggingMiddleware)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
# Optional: Enable if you use forms

# ------------------------------------------------


# ------------------- Routes ---------------------

def user_is_authenticated(request: Request):
    session_id = request.cookies.get('id')
    if not session_id:
        return False
    session = run_sync(
        Sessions.objects().where(Sessions.token == session_id).first().run()
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
    return HTMLResponse(f"""
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
    """)

# Static
app.mount('/static/', StaticFiles(directory=STATIC_DIR), name='static')

# Admin

admin = create_admin(
    tables=[
        Exhibition, ExhibitionGeo, ExhibitionDetail, ExhibitionContact,
        ExhibitionCategory, ExhibitionPrice, ExhibitionTag,
        ExhibitionTagLink, ExhibitionMedia, AdminUser,
    ],
    auth_table=AdminUser,
    session_table=Sessions,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "travelculturehub.com",
        "www.travelculturehub.com",
        "travelculture.baregorc.com",
        "www.travelculture.baregorc.com",
    ],
)

app.mount('/admin/', admin)

# REST Routers
app.include_router(custom_admin_router_api)
app.include_router(exhibition_router_view)
app.include_router(exhibition_router_view, prefix='/categories')
app.include_router(exhibition_router_view, prefix='/exhibitions')
app.include_router(exhibition_router_api)
app.include_router(admin_router_api, prefix='/admin_api')

def get_context(request: Request):
    return {"pool": request.app.state.pool}
# # GraphQL
# graphql_app = GraphQLRouter(
#     schema,
#     subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL],
#     graphiql=True,  # Set to False in production
# context_getter=get_context,
# )
# app.include_router(graphql_app, prefix='/graphql')
#
