import asyncio
import os

import os
from dotenv import load_dotenv
import logging

from api.apps.users.models import AdminUser
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

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
