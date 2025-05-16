from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

DB = PostgresEngine(
    config={
        'database': 'culture_aggregator',
        'user': 'admin',
        'password': 'postgres',
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
