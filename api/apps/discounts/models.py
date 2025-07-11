from __future__ import annotations

import logging

from piccolo.columns import (
    Array,
    Boolean,
    DoublePrecision,
    ForeignKey,
    Text,
    Timestamptz,
    Varchar, Integer, OnDelete,
)
from piccolo.table import Table

from api.apps.exhibitions.utils import now, slugify

logger = logging.getLogger(__name__)

class DiscountMeta(Table):
    created_at: Timestamptz = Timestamptz(timezone=True, default=now)
    updated_at: Timestamptz = Timestamptz(timezone=True, default=now)

    start_date: Timestamptz = Timestamptz(null=False)
    end_date: Timestamptz = Timestamptz(null=False)
    is_active: Boolean = Boolean(default=True)

    def save(self, *args, **kwargs):
        self.updated_at = now()
        return super().save(*args, **kwargs)

    class Meta:
        app_name = 'discounts'
        table_name = 'discount_meta'


class Discount(DiscountMeta):
    title: Varchar = Varchar(length=300)
    slug: Varchar = Varchar(length=300, unique=True)
    detail: ForeignKey = ForeignKey(references='DiscountDetail', on_delete=OnDelete.cascade)
    price: ForeignKey = ForeignKey(references='DiscountPrice', on_delete=OnDelete.cascade)
    media: ForeignKey = ForeignKey(references='DiscountMedia', on_delete=OnDelete.cascade)
    shop: ForeignKey = ForeignKey(references='DiscountShop', on_delete=OnDelete.cascade)
    category: ForeignKey = ForeignKey(references='DiscountCategory', on_delete=OnDelete.cascade)


    class Meta:
        app_name = 'discounts'
        table_name = 'discount'

class DiscountDetail(Table):
    description: Text = Text()

    class Meta:
        app_name = 'discounts'
        table_name = 'discount_detail'

class DiscountPrice(Table):
    new_price: DoublePrecision = DoublePrecision(null=True)
    old_price: DoublePrecision = DoublePrecision(null=True)
    percent: Integer = Integer(null=True)
    delivery_detail: Varchar = Varchar(length=100)
    is_fire_dealer: Boolean = Boolean(default=True)

    def save(self, *args, **kwargs):
        if self.old_price and self.new_price:
            self.percent = int(round((1 - self.new_price / self.old_price) * 100))
        return super().save(*args, **kwargs)

    class Meta:
        app_name = 'discounts'
        table_name = 'discount_price'

class DiscountMedia(Table):
    images = Array(base_column=Varchar(length=300), default_factory=list)

    class Meta:
        app_name = 'discounts'
        table_name = 'discount_media'

class DiscountShop(Table):
    title: Varchar = Varchar(length=300, unique=True)
    slug: Varchar = Varchar(length=300, unique=True)
    shop_link: Varchar = Varchar(length=300, unique=True)
    site_link: Varchar = Varchar(length=300, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        app_name = 'discounts'
        table_name = 'discount_shop'

class DiscountCategory(Table):
    title: Varchar = Varchar(length=200, unique=True)
    slug: Varchar = Varchar(length=200, unique=True)

    @property
    def label(self) -> str:
        return f'{self.title} ({self.slug})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        app_name = 'discounts'
        display_column = 'title'
        table_name = 'discount_category'
