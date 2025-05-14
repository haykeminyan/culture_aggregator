from piccolo_admin.endpoints import create_admin
from api.apps.exhibitions.models import Exhibition
from fastapi import FastAPI
from api.apps.users.models import AdminUser, Sessions
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="super-secret")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 🔐 Session middleware для CSRF и логина

# 🛠 Подключаем админку
admin = create_admin(
    tables=[
        Exhibition,
        AdminUser],
    auth_table=AdminUser,
    session_table=Sessions,
)

app.mount("/admin/", admin)

@app.get("/")
def read_root():
    return {"message": "Hello from culture aggregator!"}