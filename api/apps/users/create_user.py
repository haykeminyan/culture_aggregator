import asyncio

from api.apps.users.models import AdminUser


async def create():
    await AdminUser.create_user(
        username="admin",
        password="emin1996",
        email="ibhayk@gmail.com",
        admin=True,
        superuser=True,
        active=True
    )

if __name__ == "__main__":
    asyncio.run(create())