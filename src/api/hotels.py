from fastapi import APIRouter, Query, Body

from src.schemas.hotels import HotelAdd, HotelPatch
from src.api.dependencies import PaginationDep, DBDep

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("", summary="Получить список отелей")
async def get_hotels(
        db: DBDep,
        pagination: PaginationDep,
        stars: int | None = Query(None, description="Фильтр по количеству звезд"),
        title: str | None = Query(None, description="Фильтр по названию отеля"),
        location: str | None = Query(None, description="Фильтр по адресу")
):
    per_page = pagination.per_page or 5

    return await db.hotels.get_all_by_filter(
        stars=stars,
        title=title,
        location=location,
        limit=per_page,
        offset=per_page * (pagination.page - 1)
    )

@router.get("/{hotel_id}", summary="Получить отель по id")
async def get_hotel(hotel_id: int, db: DBDep):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if hotel is None:
        return {"message": "Отель не найден"}
    return hotel


@router.delete("/{hotel_id}", summary="Удалить отель")
async def delete_hotel(hotel_id: int, db: DBDep):
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"message": "Отель успешно удален"}


@router.post("", summary="Добавить отель")
async def create_hotel(
        db: DBDep,
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
    new_hotel = await db.hotels.add(hotel_data)
    await db.commit()
    return {"Status": "Ok", "data": new_hotel}


@router.put("/{hotel_id}", summary="Полное обновление данных об отеле")
async def update_hotel(
        hotel_id: int,
        hotel_data: HotelAdd,
        db: DBDep
):
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
    return {"message": "Отель успешно обновлен"}


@router.patch("/{hotel_id}", summary="Частичное обновление данных об отеле")
async def partial_update_hotel(
        hotel_id: int,
        hotel_data: HotelPatch,
        db: DBDep
):
    await db.hotels.edit(hotel_data, id=hotel_id, for_patch=True)
    await db.commit()
    return {"message": "Отель успешно обновлен"}
