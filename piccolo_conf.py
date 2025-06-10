from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

DB = PostgresEngine(
    config={
        "database": os.getenv("POSTGRES_DB", "culture_aggregator"),
        "user": os.getenv("POSTGRES_USER", "admin"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
    }
)

APP_REGISTRY = AppRegistry(
    apps=[
        'api.apps.users.piccolo_app',
        'piccolo_api.session_auth.piccolo_app',
        'api.apps.exhibitions.piccolo_app',
    ],
)
