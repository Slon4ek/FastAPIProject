from fastapi import APIRouter, Query, Body
from sqlalchemy import insert, select

from src.database import async_session_maker, engine
from src.models.hotels import HotelsModel
from src.schemas.hotels import Hotel, HotelPatch
from src.api.dependencies import PaginationDep

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("", summary="Получить список отелей")
async def get_hotels(
    pagination: PaginationDep,
    stars: int | None = Query(None, description="Фильтр по количеству звезд"),
    title: str | None = Query(None, description="Фильтр по названию отеля"),
    location: str | None = Query(None, description="Фильтр по адресу")
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        qwery = select(HotelsModel)
        if stars:
            qwery = qwery.filter_by(stars=stars)
        if title:
            qwery = qwery.filter_by(title=title)
        if location:
            qwery = qwery.filter_by(location=location)
        qwery = (
            qwery
            .limit(per_page)
            .offset(per_page * (pagination.page - 1))
        )
        result = await session.execute(qwery)
        hotels = result.scalars().all()
    return hotels


@router.delete("/{hotel_id}", summary="Удалить отель")
def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"message": "Отель успешно удален"}


@router.post("", summary="Добавить отель")
async def create_hotel(
    hotel_data: Hotel = Body(
        openapi_examples={
            "1": {
                "summary": "Hilton Hotel", "value":
                    {
                        "title": "Hilton", "stars": 5, "location": "г. Сочи, ул. Моря, д. 1"
                     }
            },
            "2":
                {
                    "summary": "Four Seasons Hotel", "value":
                    {
                        "title": "Four Seasons", "stars": 4, "location": "г. Москва, ул. Ленина, д. 1"
                     }
                 },
        }
    )
):
    async with async_session_maker() as session:
        add_hotel_stmt = insert(HotelsModel).values(**hotel_data.model_dump())
        await session.execute(add_hotel_stmt)
        # print(add_hotel_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
        await session.commit()
    return {"message": "Отель успешно добавлен"}


@router.put("/{hotel_id}", summary="Полное обновление данных об отеле")
def update_hotel(hotel_id: int, hotel_data: Hotel):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotel["title"] = hotel_data.title
            hotel["stars"] = hotel_data.stars
            return {"message": "Отель успешно обновлен"}
    return {"message": "Отель не найден"}


@router.patch("/{hotel_id}", summary="Частичное обновление данных об отеле")
def partial_update_hotel(hotel_id: int, hotel_data: HotelPatch):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            if hotel_data.title:
                hotel["title"] = hotel_data.title
            if hotel_data.stars:
                hotel["stars"] = hotel_data.stars
            return {"message": "Отель успешно обновлен"}
    return {"message": "Отель не найден"}
