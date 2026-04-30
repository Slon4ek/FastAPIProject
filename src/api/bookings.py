from fastapi.exceptions import HTTPException

from fastapi import APIRouter
from starlette import status

from src.exceptions import NotFoundError, NotAvailableError
from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd

router = APIRouter(prefix="/bookings", tags=["Бронирование номеров"])


@router.get("", summary="Все бронирования", description="Получение бронирований всех пользователей")
async def get_all_bookings(db: DBDep):
    return await db.bookings.get_all()


@router.get(
    "/me",
    summary="Бронирования пользователя",
    description="Получение бронирований текущего пользователя",
)
async def get_my_bookings(user_id: UserIdDep, db: DBDep):
    return await db.bookings.get_all_by_filter(user_id=user_id)


@router.post(
    "",
    summary="Создать бронирование",
    description="Бронирование номера в отеле на определенные даты",
)
async def create_booking(user_id: UserIdDep, db: DBDep, booking_data: BookingAddRequest):
    try:
        room = await db.rooms.get_one(id=booking_data.room_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Номер не найден")

    _booking_data = BookingAdd(user_id=user_id, price=room.price, **booking_data.model_dump())
    try:
        booking = await db.bookings.add_booking(data=_booking_data, hotel_id=room.hotel_id)
    except NotAvailableError:
        raise HTTPException(
            status_code=409, detail="Не осталось свободных номеров на указанные даты"
        )
    await db.commit()

    return {"message": "Бронирование успешно создано", "booking": booking}
