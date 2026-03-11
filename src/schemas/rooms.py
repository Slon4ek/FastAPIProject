from pydantic import BaseModel, Field


class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str
    price: int
    quantity: int


class Room(RoomAdd):
    id: int

class RoomEdit(BaseModel):
    title: str = Field(None, description="Название номера")
    description: str = Field(None, description="Описание номера")
    price: int = Field(None, description="Цена за ночь")
    quantity: int = Field(None, description="Количество номеров")