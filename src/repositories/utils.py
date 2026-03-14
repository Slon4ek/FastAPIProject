from datetime import date
from sqlalchemy import select, func

from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm


def get_available_rooms(
        date_from: date,
        date_to: date,
        hotel_id: int | None = None
):
    booked_rooms_count = (
        select(BookingsOrm.room_id, func.count("*").label("rooms_booked"))
        .select_from(BookingsOrm)
        .filter(
            BookingsOrm.date_from <= date_to,
            BookingsOrm.date_to >= date_from
        )
        .group_by(BookingsOrm.room_id)
        .cte("booked_rooms_count")
    )

    a_rooms_table = (
        select(
            RoomsOrm.id.label("room_id"),
            (RoomsOrm.quantity - func.coalesce(booked_rooms_count.c.rooms_booked, 0)).label("available_rooms")
        )
        .select_from(RoomsOrm)
        .outerjoin(booked_rooms_count, RoomsOrm.id == booked_rooms_count.c.room_id)
        .cte("a_room_table")
    )

    rooms_ids_for_hotel = (
        select(RoomsOrm.id)
        .select_from(RoomsOrm)
    )
    if hotel_id:
        rooms_ids_for_hotel = rooms_ids_for_hotel.filter_by(hotel_id=hotel_id)

    rooms_ids_for_hotel = rooms_ids_for_hotel.subquery(name="rooms_ids_for_hotel")

    if not hotel_id:
        rooms_ids_for_get = select(a_rooms_table.c.room_id)
    else:
        rooms_ids_for_get = select(a_rooms_table)

    rooms_ids_for_get = (
        rooms_ids_for_get
        .select_from(a_rooms_table)
        .filter(
            a_rooms_table.c.available_rooms > 0,
            a_rooms_table.c.room_id.in_(select(rooms_ids_for_hotel))
        )
    )
    return rooms_ids_for_get