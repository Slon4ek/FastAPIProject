from pydantic import BaseModel, Field, ConfigDict


class HotelAdd(BaseModel):
    title: str
    stars: int
    location: str

class Hotel(HotelAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)

class HotelPatch(BaseModel):
    title: str = Field(None, description="Название отеля")
    stars: int = Field(None, description="Количество звезд")
    location: str = Field(None, description="Адрес отеля")
