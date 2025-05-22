from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Serial
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


class ExhibitionCategory(Table, tablename="exhibition_category", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


class ExhibitionDetails(Table, tablename="exhibition_details", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


class ExhibitionGeo(Table, tablename="exhibition_geo", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


ID = "2025-05-22T00:00:07:582407"
VERSION = "1.25.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="exhibitions", description=DESCRIPTION
    )

    manager.add_column(
        table_class_name="Exhibition",
        tablename="exhibition",
        column_name="contact",
        db_column_name="contact",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": "ExhibitionContacts",
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.alter_column(
        table_class_name="Exhibition",
        tablename="exhibition",
        column_name="category",
        db_column_name="category",
        params={"references": ExhibitionCategory},
        old_params={"references": ExhibitionCategory},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    manager.alter_column(
        table_class_name="Exhibition",
        tablename="exhibition",
        column_name="geo",
        db_column_name="geo",
        params={"references": ExhibitionGeo},
        old_params={"references": ExhibitionGeo},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    manager.alter_column(
        table_class_name="Exhibition",
        tablename="exhibition",
        column_name="details",
        db_column_name="details",
        params={"references": ExhibitionDetails},
        old_params={"references": ExhibitionDetails},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    return manager
