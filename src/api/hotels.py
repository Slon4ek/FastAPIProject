from fastapi import APIRouter, Query, Body

from src.database import async_session_maker
from src.repositories.hotels import HotelsRepository
from src.schemas.hotels import HotelAdd, HotelPatch
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
        return await HotelsRepository(session).get_all(
            stars=stars,
            title=title,
            location=location,
            limit=per_page,
            offset=per_page * (pagination.page - 1)
        )

@router.get("/{hotel_id}", summary="Получить отель по id")
async def get_hotel(hotel_id: int):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).get_by_id(hotel_id)
    return hotel


@router.delete("/{hotel_id}", summary="Удалить отель")
async def delete_hotel(hotel_id: int):
    async with async_session_maker() as session:
        await HotelsRepository(session).delete(id=hotel_id)
        await session.commit()
    return {"message": "Отель успешно удален"}


@router.post("", summary="Добавить отель")
async def create_hotel(
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "Hilton Hotel": {
                "summary": "Hilton Hotel",
                "value": {
                    "title": "Hilton",
                    "stars": 5,
                    "location": "г. Сочи, ул. Моря, д. 1"
                }
            },
            "Four Seasons Hotel": {
                "summary": "Four Seasons Hotel",
                "value": {
                    "title": "Four Seasons",
                    "stars": 4,
                    "location": "г. Москва, ул. Ленина, д. 1"
                }
            }
        }

    )
):
    async with async_session_maker() as session:
        new_hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()
    return {"Status": "Ok", "data": new_hotel}


@router.put("/{hotel_id}", summary="Полное обновление данных об отеле")
async def update_hotel(hotel_id: int, hotel_data: HotelAdd):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(hotel_data, id=hotel_id)
        await session.commit()
    return {"message": "Отель успешно обновлен"}


@router.patch("/{hotel_id}", summary="Частичное обновление данных об отеле")
async def partial_update_hotel(hotel_id: int, hotel_data: HotelPatch):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(hotel_data, id=hotel_id, for_patch=True)
        await session.commit()
    return {"message": "Отель успешно обновлен"}
