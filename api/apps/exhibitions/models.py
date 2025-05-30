from __future__ import annotations

from piccolo.columns import (
    Boolean,
    DoublePrecision,
    ForeignKey,
    Text,
    Timestamptz,
    Varchar, JSON, Array,
)
from piccolo.table import Table

from api.apps.exhibitions.utils import now, slugify
import logging

logger = logging.getLogger(__name__)

class ExhibitionMeta(Table):
    created_at: Timestamptz = Timestamptz(timezone=True, default=now)
    updated_at: Timestamptz = Timestamptz(timezone=True, default=now)

    start_date: Timestamptz = Timestamptz(null=False)
    end_date: Timestamptz = Timestamptz(null=False)
    is_active: Boolean = Boolean(default=True)

    def save(self, *args, **kwargs):
        self.updated_at = now()
        return super().save(*args, **kwargs)

    class Meta:
        app_name = 'exhibitions'
        table_name = 'exhibition_meta'


# Main features of exhibition
class Exhibition(ExhibitionMeta):
    title: Varchar = Varchar(length=200)
    slug: Varchar = Varchar(length=200, unique=True)
    short_description: Varchar = Varchar(length=200)

    category: ForeignKey = ForeignKey(references='ExhibitionCategory')
    geo: ForeignKey = ForeignKey(references='ExhibitionGeo')
    detail: ForeignKey = ForeignKey(references='ExhibitionDetail')
    contact: ForeignKey = ForeignKey(references='ExhibitionContact')
    media: ForeignKey = ForeignKey(references='ExhibitionMedia')
    price: ForeignKey = ForeignKey(references='ExhibitionPrice')
    organizer: ForeignKey = ForeignKey(references='ExhibitionOrganizer')


    # TODO need to add for all fields this validations as schemas only for /docs... not for FUCKING PICCOLO
    def validate(self):
        if not self.title:
            logger.error('Title cannot be empty')
            raise ValueError("Title can not be empty")
        elif ' ' in self.slug:
            logger.error('Slug must be non-empty and without spaces.')
            raise ValueError("Slug must be non-empty and without spaces.")

    def save(self, *args, **kwargs):
        self.validate()
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        app_name = 'exhibitions'
        table_name = 'exhibition'


class ExhibitionPrice(Table):
    price: Varchar = Varchar(length=100, null=True)
    currency: Varchar = Varchar(length=100, null=True, default='AMD')

    def save(self, *args, **kwargs):
        self.currency = self.currency.upper()
        return super().save(*args, **kwargs)

    class Meta:
        app_name = 'exhibitions'
        table_name = 'exhibition_price'

class ExhibitionOrganizer(Table):
    name: Varchar = Varchar(length=200, null=True)

    class Meta:
        app_name = 'exhibitions'
        table_name = 'exhibition_organizer'


class ExhibitionContact(Table):
    website: Varchar = Varchar(length=200)
    youtube: Varchar = Varchar(length=200)
    linkedin: Varchar = Varchar(length=200)
    tiktok: Varchar = Varchar(length=200)
    instagram: Varchar = Varchar(length=200)

    class Meta:
        app_name = 'exhibitions'
        table_name = 'exhibition_contact'

class ExhibitionMedia(Table):
    images = Array(base_column=Varchar(length=300), default_factory=list)


# Geolocation
class ExhibitionGeo(Table):
    location: Varchar = Varchar(length=200)
    latitude: DoublePrecision = DoublePrecision()
    longitude: DoublePrecision = DoublePrecision()
    country: Varchar = Varchar(length=200)
    city: Varchar = Varchar(length=200)

    class Meta:
        app_name = 'exhibitions'
        table_name = 'exhibition_geo'

    def __str__(self):
        return self.location


class ExhibitionDetail(Table):
    description: Text = Text()

    class Meta:
        app_name = 'exhibitions'
        table_name = 'exhibition_detail'


class ExhibitionCategory(Table):
    title: Varchar = Varchar(length=200, unique=True)
    slug: Varchar = Varchar(length=200, unique=True)

    @property
    def label(self) -> str:
        return f"{self.title} ({self.slug})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        app_name = 'exhibitions'
        display_column = "title"
        table_name = 'exhibition_category'


class ExhibitionTag(Table):
    tag: Varchar = Varchar(length=200)
    slug: Varchar = Varchar(length=200, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.tag)
        return super().save(*args, **kwargs)

    class Meta:
        app_name = 'exhibitions'


# Many-to-Many
class ExhibitionTagLink(Table):
    exhibition: ForeignKey = ForeignKey(references=Exhibition)
    tag: ForeignKey = ForeignKey(references=ExhibitionTag)

    class Meta:
        app_name = 'exhibitions'
