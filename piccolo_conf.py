from piccolo.engine.postgres import PostgresEngine
from piccolo.conf.apps import AppRegistry

DB = PostgresEngine(config={
    "database": "culture_aggregator",
    "user": "admin",
    "password": "postgres",
    "host": "postgres",
    "port": 5432,
})

APP_REGISTRY = AppRegistry(
    apps=[
        'api.apps.users.piccolo_app',
        'api.apps.exhibitions.piccolo_app',
    ]
)
