from src.schemas.bookings import BookingAdd


async def test_bookings_crud(db):
    from datetime import date

    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id

    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        price=1000,
        date_from=date(year=2026, month=12, day=28),
        date_to=date(year=2027, month=1, day=5),
    )

    new_booking = await db.bookings.add(booking_data)
    booking = await db.bookings.get_one_or_none(id=new_booking.id)

    assert booking
    assert booking.user_id == user_id
    assert booking.room_id == room_id
    assert booking.price == 1000

    new_date_to = date(year=2027, month=1, day=10)
    update_booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        price=1000,
        date_from=date(year=2026, month=12, day=28),
        date_to=new_date_to,
    )
    await db.bookings.edit(data=update_booking_data, id=booking.id)

    updated_booking = await db.bookings.get_one_or_none(id=booking.id)
    assert updated_booking
    assert updated_booking.date_to == new_date_to

    await db.bookings.delete(id=booking.id)
    assert not await db.bookings.get_one_or_none(id=booking.id)
    await db.rollback()
