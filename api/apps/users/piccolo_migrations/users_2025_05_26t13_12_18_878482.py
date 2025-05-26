from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2025-05-26T13:12:18:878482"
VERSION = "1.25.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="", description=DESCRIPTION
    )

    def run():
        print(f"running {ID}")

    manager.add_raw(run)

    return manager
