from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Serial
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


class Exhibition(Table, tablename="exhibition", schema=None):
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


class ExhibitionContacts(Table, tablename="exhibition_contacts", schema=None):
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


class ExhibitionMedia(Table, tablename="exhibition_media", schema=None):
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


ID = "2025-05-29T17:29:20:079056"
VERSION = "1.25.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="exhibitions", description=DESCRIPTION
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

    manager.alter_column(
        table_class_name="Exhibition",
        tablename="exhibition",
        column_name="contacts",
        db_column_name="contacts",
        params={"references": ExhibitionContacts},
        old_params={"references": ExhibitionContacts},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    manager.alter_column(
        table_class_name="Exhibition",
        tablename="exhibition",
        column_name="media",
        db_column_name="media",
        params={"references": ExhibitionMedia},
        old_params={"references": ExhibitionMedia},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    manager.alter_column(
        table_class_name="ExhibitionOrganizer",
        tablename="exhibition_organizer",
        column_name="exhibition",
        db_column_name="exhibition",
        params={"references": Exhibition},
        old_params={"references": Exhibition},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    manager.alter_column(
        table_class_name="ExhibitionPeriod",
        tablename="exhibition_period",
        column_name="exhibition",
        db_column_name="exhibition",
        params={"references": Exhibition},
        old_params={"references": Exhibition},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    manager.alter_column(
        table_class_name="ExhibitionPrice",
        tablename="exhibition_price",
        column_name="exhibition",
        db_column_name="exhibition",
        params={"references": Exhibition},
        old_params={"references": Exhibition},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    return manager
