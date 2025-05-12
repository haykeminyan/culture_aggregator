from piccolo_admin.endpoints import create_admin
from api.apps.exhibitions.models import CulturalSite
from fastapi import FastAPI
from api.apps.users.models import AdminUser, Sessions
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="super-secret")

# 🔐 Session middleware для CSRF и логина

# 🛠 Подключаем админку
admin = create_admin(
    tables=[CulturalSite],
    auth_table=AdminUser,  # 👈 здесь кастомная модель
    session_table=Sessions,
)

app.mount("/admin/", admin)

@app.get("/")
def read_root():
    return {"message": "Hello from culture aggregator!"}