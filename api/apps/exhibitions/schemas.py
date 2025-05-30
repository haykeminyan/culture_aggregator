from datetime import datetime, timezone

from pydantic import BaseModel, HttpUrl, PrivateAttr


class ExhibitionCreateGeo(BaseModel):
    location: str | None = None
    latitude: float
    longitude: float
    country: str
    city: str


class ExhibitionCreateCategory(BaseModel):
    title: str
    slug: str


class ExhibitionCreateDetails(BaseModel):
    description: str


class ExhibitionContactsIn(BaseModel):
    youtube: HttpUrl
    linkedin: HttpUrl


class ExhibitionCreate(BaseModel):
    title: str
    slug: str
    short_description: str
    image: list[str]
    category: ExhibitionCreateCategory
    geo: ExhibitionCreateGeo
    details: ExhibitionCreateDetails


class ExhibitionUpdate(BaseModel):
    title: str
    _updated_at: datetime = PrivateAttr(default_factory=lambda: datetime.now(timezone.utc))
    short_description: str
    category: ExhibitionCreateCategory
    geo: ExhibitionCreateGeo
    details: ExhibitionCreateDetails
