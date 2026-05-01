from fastapi.exceptions import HTTPException

from fastapi import APIRouter

from src.exceptions import NotFoundError, NotAvailableError, RoomNotFoundHTTPException
from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирование номеров"])


@router.get("", summary="Все бронирования", description="Получение бронирований всех пользователей")
async def get_all_bookings(db: DBDep):
    return await BookingService(db).get_all_bookings()


@router.get(
    "/me",
    summary="Бронирования пользователя",
    description="Получение бронирований текущего пользователя",
)
async def get_my_bookings(user_id: UserIdDep, db: DBDep):
    return await BookingService(db).get_user_bookings(user_id=user_id)


@router.post(
    "",
    summary="Создать бронирование",
    description="Бронирование номера в отеле на определенные даты",
)
async def create_booking(user_id: UserIdDep, db: DBDep, booking_data: BookingAddRequest):
    try:
        booking = await BookingService(db).create_booking(data=booking_data, user_id=user_id)
    except NotFoundError:
        raise RoomNotFoundHTTPException
    except NotAvailableError:
        raise HTTPException(
            status_code=409, detail="Не осталось свободных номеров на указанные даты"
        )
    return {"message": "Бронирование успешно создано", "booking": booking}
