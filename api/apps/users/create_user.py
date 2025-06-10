import asyncio
import os

from api.apps.users.models import AdminUser
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()


async def create():
    await AdminUser.create_user(
        username='admin',
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        email='ibhayk@gmail.com',
        admin=True,
        superuser=True,
        active=True,
    )


if __name__ == '__main__':
    asyncio.run(create())
