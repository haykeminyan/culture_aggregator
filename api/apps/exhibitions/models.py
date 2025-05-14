from __future__ import annotations

from piccolo.table import Table
from piccolo.columns import (
    Varchar,
    Text,
    Timestamptz,
    Boolean,
    DoublePrecision,
    ForeignKey,
)

from api.apps.exhibitions.utils import now, slugify

class ExhibitionMeta(Table):
    created_at: Timestamptz = Timestamptz(timezone=True, default=now)
    updated_at: Timestamptz = Timestamptz(timezone=True, default=now)
    is_active: Boolean = Boolean(default=True)

    def save(self, *args, **kwargs):
        self.updated_at = now()
        return super().save(*args, **kwargs)


# Main features of exhibition
class Exhibition(ExhibitionMeta):
    title: Varchar = Varchar(length=200)
    slug: Varchar = Varchar(length=200, unique=True)
    short_description: Varchar = Varchar(length=200)
    category: ForeignKey = ForeignKey(references="ExhibitionCategory")
    geo: ForeignKey = ForeignKey(references="ExhibitionGeo")
    details: ForeignKey = ForeignKey(references="ExhibitionDetails")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)  # ⛔️ не await, а return


# Geolocation
class ExhibitionGeo(Table):
    location: Varchar = Varchar(length=200)
    latitude: DoublePrecision = DoublePrecision()
    longitude: DoublePrecision = DoublePrecision()
    country: Varchar = Varchar(length=200)
    city: Varchar = Varchar(length=200)


class ExhibitionDetails(Table):
    description: Text = Text()


class ExhibitionCategory(Table):
    title: Varchar = Varchar(length=200)
    slug: Varchar = Varchar(length=200, unique=True)


class ExhibitionTag(Table):
    tag: Varchar = Varchar(length=200)
    slug: Varchar = Varchar(length=200, unique=True)


# Many-to-Many
class ExhibitionTagLink(Table):
    exhibition: ForeignKey = ForeignKey(references=Exhibition)
    tag: ForeignKey = ForeignKey(references=ExhibitionTag)
