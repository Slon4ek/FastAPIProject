from fastapi import APIRouter

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd

router = APIRouter(prefix="/bookings", tags=["Бронирование номеров"])


@router.get(
    "",
    summary="Все бронирования",
    description="Получение бронирований всех пользователей"
)
async def get_all_bookings(
        db: DBDep
):
    return await db.bookings.get_all()


@router.get(
    "/me",
    summary="Бронирования пользователя",
    description="Получение бронирований текущего пользователя"
)
async def get_my_bookings(
        user_id: UserIdDep,
        db: DBDep
):
    return await db.bookings.get_all_by_filter(user_id=user_id)


@router.post(
    "",
    summary="Создать бронирование",
    description="Бронирование номера в отеле на определенные даты"
)
async def create_booking(
        user_id: UserIdDep,
        db: DBDep,
        booking_data: BookingAddRequest
):
    room = await db.rooms.get_one_or_none(id=booking_data.room_id, hotel_id=booking_data.hotel_id)

    if room is None:
        return {"message": "Номер не найден"}

    _booking_data = BookingAdd(user_id=user_id, price=room.price, **booking_data.model_dump())
    booking = await db.bookings.add(_booking_data)
    await db.commit()

    return {"message": "Бронирование успешно создано", "booking": booking}
