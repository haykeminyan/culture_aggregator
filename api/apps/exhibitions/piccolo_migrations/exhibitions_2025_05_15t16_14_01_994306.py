from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete, OnUpdate
from piccolo.columns.column_types import (
    Boolean,
    DoublePrecision,
    ForeignKey,
    Serial,
    Text,
    Timestamptz,
    Varchar,
)
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table

from api.apps.exhibitions.utils import now


class Exhibition(Table, tablename='exhibition', schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name='id',
        secret=False,
    )


class ExhibitionTag(Table, tablename='exhibition_tag', schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name='id',
        secret=False,
    )


ID = '2025-05-15T16:14:01:994306'
VERSION = '1.25.0'
DESCRIPTION = ''


async def forwards():
    manager = MigrationManager(
        migration_id=ID,
        app_name='exhibitions',
        description=DESCRIPTION,
    )

    manager.add_table(
        class_name='Exhibition',
        tablename='exhibition',
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name='ExhibitionCategory',
        tablename='exhibition_category',
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name='ExhibitionTag',
        tablename='exhibition_tag',
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name='ExhibitionGeo',
        tablename='exhibition_geo',
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name='ExhibitionDetails',
        tablename='exhibition_details',
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name='ExhibitionMeta',
        tablename='exhibition_meta',
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name='ExhibitionTagLink',
        tablename='exhibition_tag_link',
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name='Exhibition',
        tablename='exhibition',
        column_name='created_at',
        db_column_name='created_at',
        column_class_name='Timestamptz',
        column_class=Timestamptz,
        params={
            'timezone': True,
            'default': now,
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='Exhibition',
        tablename='exhibition',
        column_name='updated_at',
        db_column_name='updated_at',
        column_class_name='Timestamptz',
        column_class=Timestamptz,
        params={
            'timezone': True,
            'default': now,
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='Exhibition',
        tablename='exhibition',
        column_name='is_active',
        db_column_name='is_active',
        column_class_name='Boolean',
        column_class=Boolean,
        params={
            'default': True,
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='Exhibition',
        tablename='exhibition',
        column_name='id',
        db_column_name='id',
        column_class_name='Serial',
        column_class=Serial,
        params={
            'null': False,
            'primary_key': True,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': 'id',
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='Exhibition',
        tablename='exhibition',
        column_name='title',
        db_column_name='title',
        column_class_name='Varchar',
        column_class=Varchar,
        params={
            'length': 200,
            'default': '',
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='Exhibition',
        tablename='exhibition',
        column_name='slug',
        db_column_name='slug',
        column_class_name='Varchar',
        column_class=Varchar,
        params={
            'length': 200,
            'default': '',
            'null': False,
            'primary_key': False,
            'unique': True,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='Exhibition',
        tablename='exhibition',
        column_name='short_description',
        db_column_name='short_description',
        column_class_name='Varchar',
        column_class=Varchar,
        params={
            'length': 200,
            'default': '',
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='Exhibition',
        tablename='exhibition',
        column_name='category',
        db_column_name='category',
        column_class_name='ForeignKey',
        column_class=ForeignKey,
        params={
            'references': 'ExhibitionCategory',
            'on_delete': OnDelete.cascade,
            'on_update': OnUpdate.cascade,
            'target_column': None,
            'null': True,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='Exhibition',
        tablename='exhibition',
        column_name='geo',
        db_column_name='geo',
        column_class_name='ForeignKey',
        column_class=ForeignKey,
        params={
            'references': 'ExhibitionGeo',
            'on_delete': OnDelete.cascade,
            'on_update': OnUpdate.cascade,
            'target_column': None,
            'null': True,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='Exhibition',
        tablename='exhibition',
        column_name='details',
        db_column_name='details',
        column_class_name='ForeignKey',
        column_class=ForeignKey,
        params={
            'references': 'ExhibitionDetails',
            'on_delete': OnDelete.cascade,
            'on_update': OnUpdate.cascade,
            'target_column': None,
            'null': True,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionCategory',
        tablename='exhibition_category',
        column_name='title',
        db_column_name='title',
        column_class_name='Varchar',
        column_class=Varchar,
        params={
            'length': 200,
            'default': '',
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionCategory',
        tablename='exhibition_category',
        column_name='slug',
        db_column_name='slug',
        column_class_name='Varchar',
        column_class=Varchar,
        params={
            'length': 200,
            'default': '',
            'null': False,
            'primary_key': False,
            'unique': True,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionTag',
        tablename='exhibition_tag',
        column_name='tag',
        db_column_name='tag',
        column_class_name='Varchar',
        column_class=Varchar,
        params={
            'length': 200,
            'default': '',
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionTag',
        tablename='exhibition_tag',
        column_name='slug',
        db_column_name='slug',
        column_class_name='Varchar',
        column_class=Varchar,
        params={
            'length': 200,
            'default': '',
            'null': False,
            'primary_key': False,
            'unique': True,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionGeo',
        tablename='exhibition_geo',
        column_name='location',
        db_column_name='location',
        column_class_name='Varchar',
        column_class=Varchar,
        params={
            'length': 200,
            'default': '',
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionGeo',
        tablename='exhibition_geo',
        column_name='latitude',
        db_column_name='latitude',
        column_class_name='DoublePrecision',
        column_class=DoublePrecision,
        params={
            'default': 0.0,
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionGeo',
        tablename='exhibition_geo',
        column_name='longitude',
        db_column_name='longitude',
        column_class_name='DoublePrecision',
        column_class=DoublePrecision,
        params={
            'default': 0.0,
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionGeo',
        tablename='exhibition_geo',
        column_name='country',
        db_column_name='country',
        column_class_name='Varchar',
        column_class=Varchar,
        params={
            'length': 200,
            'default': '',
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionGeo',
        tablename='exhibition_geo',
        column_name='city',
        db_column_name='city',
        column_class_name='Varchar',
        column_class=Varchar,
        params={
            'length': 200,
            'default': '',
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionDetails',
        tablename='exhibition_details',
        column_name='description',
        db_column_name='description',
        column_class_name='Text',
        column_class=Text,
        params={
            'default': '',
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionMeta',
        tablename='exhibition_meta',
        column_name='created_at',
        db_column_name='created_at',
        column_class_name='Timestamptz',
        column_class=Timestamptz,
        params={
            'timezone': True,
            'default': now,
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionMeta',
        tablename='exhibition_meta',
        column_name='updated_at',
        db_column_name='updated_at',
        column_class_name='Timestamptz',
        column_class=Timestamptz,
        params={
            'timezone': True,
            'default': now,
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionMeta',
        tablename='exhibition_meta',
        column_name='is_active',
        db_column_name='is_active',
        column_class_name='Boolean',
        column_class=Boolean,
        params={
            'default': True,
            'null': False,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionTagLink',
        tablename='exhibition_tag_link',
        column_name='exhibition',
        db_column_name='exhibition',
        column_class_name='ForeignKey',
        column_class=ForeignKey,
        params={
            'references': Exhibition,
            'on_delete': OnDelete.cascade,
            'on_update': OnUpdate.cascade,
            'target_column': None,
            'null': True,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name='ExhibitionTagLink',
        tablename='exhibition_tag_link',
        column_name='tag',
        db_column_name='tag',
        column_class_name='ForeignKey',
        column_class=ForeignKey,
        params={
            'references': ExhibitionTag,
            'on_delete': OnDelete.cascade,
            'on_update': OnUpdate.cascade,
            'target_column': None,
            'null': True,
            'primary_key': False,
            'unique': False,
            'index': False,
            'index_method': IndexMethod.btree,
            'choices': None,
            'db_column_name': None,
            'secret': False,
        },
        schema=None,
    )

    return manager
