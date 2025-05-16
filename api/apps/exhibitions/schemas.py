from pydantic import BaseModel


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
