from datetime import date, timedelta

from pydantic import BaseModel, Field, ConfigDict

from src.schemas.images import Image
from src.schemas.rooms import Room


class HotelAdd(BaseModel):
    title: str = Field(min_length=1)
    stars: int = Field(ge=1, le=5)
    location: str = Field(min_length=1)


class Hotel(HotelAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HotelWithRelations(Hotel):
    rooms: list[Room]
    images: list[Image]


class HotelPatch(BaseModel):
    title: str | None = Field(None, description="Название отеля", min_length=1)
    stars: int | None = Field(None, description="Количество звезд", ge=1, le=5)
    location: str | None = Field(None, description="Адрес отеля", min_length=1)


class HotelsGetRequest(BaseModel):
    date_from: date | None = Field(None, examples=[date.today()], description="Дата заезда")
    date_to: date | None = Field(
        None, examples=[date.today() + timedelta(days=1)], description="Дата выезда"
    )
    stars: int | None = (Field(None, description="Количество звезд", ge=1, le=5),)
    title: str | None = (Field(None, description="Название отеля", min_length=1),)
    location: str | None = (Field(None, description="Адрес отеля", min_length=1),)
