from datetime import datetime

import strawberry


@strawberry.type
class ExhibitionGeo:
    location: str
    latitude: float
    longitude: float
    country: str
    city: str

    @classmethod
    def from_dict(cls, data: dict) -> 'ExhibitionGeo':
        return cls(
            location=data['location'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            country=data['country'],
            city=data['city'],
        )


@strawberry.type
class ExhibitionCategory:
    title: str
    slug: str

    @classmethod
    def from_dict(cls, data: dict) -> 'ExhibitionCategory':
        return cls(title=data['title'], slug=data['slug'])


@strawberry.type
class ExhibitionDetail:
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> 'ExhibitionDetail':
        return cls(description=data['description'])


@strawberry.type
class Exhibition:
    title: str
    slug: str
    short_description: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    id: str
    category: ExhibitionCategory
    geo: ExhibitionGeo
    details: ExhibitionDetail

    @classmethod
    def from_dict(cls, data: dict) -> 'Exhibition':
        return cls(
            id=str(data['id']),
            title=data['title'],
            slug=data['slug'],
            short_description=data['short_description'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            is_active=data['is_active'],
            category=ExhibitionCategory.from_dict(data['category']),
            geo=ExhibitionGeo.from_dict(data['geo']),
            details=ExhibitionDetail.from_dict(data['details']),
        )


@strawberry.input
class ExhibitionGeoInput:
    location: str
    latitude: float
    longitude: float
    country: str
    city: str


@strawberry.input
class ExhibitionCategoryInput:
    title: str
    slug: str


@strawberry.input
class ExhibitionDetailsInput:
    description: str


@strawberry.input
class ExhibitionCreateInput:
    title: str
    slug: str
    short_description: str
    category: ExhibitionCategoryInput
    geo: ExhibitionGeoInput
    details: ExhibitionDetailsInput


@strawberry.input
class ExhibitionUpdateInput:
    title: str
    short_description: str
    category: ExhibitionCategoryInput
    geo: ExhibitionGeoInput
    details: ExhibitionDetailsInput
