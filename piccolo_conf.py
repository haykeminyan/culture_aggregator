from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine
import os
from dotenv import load_dotenv
load_dotenv()

DB = PostgresEngine(
    config={
        'database': os.environ['POSTGRES_DB'],
        'user': os.environ['POSTGRES_USER'],
        'password': os.environ['POSTGRES_PASSWORD'],
        'host': 'postgres',
        'port': 5432,
    },
)

APP_REGISTRY = AppRegistry(
    apps=[
        'api.apps.users.piccolo_app',
        'piccolo_api.session_auth.piccolo_app',
        'api.apps.exhibitions.piccolo_app',
    ],
)

print("🔍 POSTGRES_USER =", os.environ.get("POSTGRES_USER"))
