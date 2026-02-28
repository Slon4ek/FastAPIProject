from pydantic import BaseModel, Field

class Hotel(BaseModel):
    title: str
    stars: int

class HotelPatch(BaseModel):
    title: str = Field(None, description='Название отеля')
    stars: int = Field(None, description='Количество звезд')