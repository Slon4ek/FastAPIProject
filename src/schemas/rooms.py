from pydantic import BaseModel, ConfigDict, Field

from src.schemas.facility import Facility
from src.schemas.images import Image


class RoomAddRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = Field(None, min_length=1)
    price: int = Field(ge=0)
    quantity: int = Field(ge=0)
    facilities_ids: list[int] = []


class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str | None = None
    price: int
    quantity: int


class Room(RoomAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomWithRelations(Room):
    facilities: list[Facility]
    images: list[Image]


class RoomEdit(BaseModel):
    title: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    price: int | None = Field(None, ge=0)
    quantity: int | None = Field(None, ge=0)
    facilities_ids: list[int] | None = []


class RoomForPatch(BaseModel):
    hotel_id: int | None = None
    title: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    price: int | None = Field(None, ge=0)
    quantity: int | None = Field(None, ge=0)
