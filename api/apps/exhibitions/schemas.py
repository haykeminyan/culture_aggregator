from pydantic import BaseModel, Field, PrivateAttr
from datetime import datetime, timezone


class ExhibitionCreateGeo(BaseModel):
    location: str | None = None
    latitude: float
    longitude: float
    country: str
    city: str


class ExhibitionCreateCategory(BaseModel):
    title: str
    slug: str | None = None


class ExhibitionCreateDetails(BaseModel):
    description: str


class ExhibitionCreate(BaseModel):
    title: str
    slug: str
    short_description: str
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
