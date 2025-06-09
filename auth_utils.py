import logging
from fastapi import FastAPI, Request
from piccolo.utils.sync import run_sync
from starlette.responses import  RedirectResponse
from starlette.status import HTTP_302_FOUND
from fastapi import Depends, APIRouter, Query, Request, HTTPException, status
from api.apps.users.models import  Sessions
logger = logging.getLogger(__name__)


def user_is_authenticated(request):
    session_id = request.cookies.get('id')
    if not session_id:
        return False

    session = run_sync(
        Sessions.objects().where(Sessions.token == session_id).first().run(),
    )
    return session is not None and not session.has_expired

async def auth_dependency(request: Request):
    if not user_is_authenticated(request):
        return RedirectResponse(url="/admin/", status_code=HTTP_302_FOUND)

async def auth_dependency_router(request: Request):
    if not user_is_authenticated(request):
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Redirect to /admin/",
            headers={"Location": "/admin/"}
        )