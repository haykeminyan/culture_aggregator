
from fastapi import Depends
from fastapi.responses import RedirectResponse
from piccolo.apps.user.tables import BaseUser
from piccolo_admin.example.tables import Sessions
from starlette.requests import Request

from api.apps.users.models import AdminUser
import logging

logger = logging.getLogger(__name__)


async def require_admin_user(request: Request):
    session_token = request.cookies.get("id")
    if not session_token:
        return RedirectResponse(url="/admin/login/?redirect=/docs", status_code=302)

    session = await Sessions.objects().where(Sessions.token == session_token).first()
    if not session:
        return RedirectResponse(url="/admin/login/?redirect=/docs", status_code=302)

    user = await AdminUser.objects().where(AdminUser.id == session.user).first()
    if not user:
        return RedirectResponse(url="/admin/login/?redirect=/docs", status_code=302)

    return user
