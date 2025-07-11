from piccolo.apps.migrations.auto.migration_manager import MigrationManager
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


class ExhibitionContact(Table, tablename="exhibition_contact", schema=None):
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


class ExhibitionDetail(Table, tablename="exhibition_detail", schema=None):
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


class ExhibitionOrganizer(Table, tablename="exhibition_organizer", schema=None):
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


class ExhibitionPrice(Table, tablename="exhibition_price", schema=None):
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


ID = "2025-07-11T13:40:38:073428"
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
        column_name="detail",
        db_column_name="detail",
        params={"references": ExhibitionDetail},
        old_params={"references": ExhibitionDetail},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    manager.alter_column(
        table_class_name="Exhibition",
        tablename="exhibition",
        column_name="contact",
        db_column_name="contact",
        params={"references": ExhibitionContact},
        old_params={"references": ExhibitionContact},
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
        table_class_name="Exhibition",
        tablename="exhibition",
        column_name="price",
        db_column_name="price",
        params={"references": ExhibitionPrice},
        old_params={"references": ExhibitionPrice},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    manager.alter_column(
        table_class_name="Exhibition",
        tablename="exhibition",
        column_name="organizer",
        db_column_name="organizer",
        params={"references": ExhibitionOrganizer},
        old_params={"references": ExhibitionOrganizer},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    return manager
