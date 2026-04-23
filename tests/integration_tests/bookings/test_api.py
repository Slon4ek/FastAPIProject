import pytest


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        (2, "2026-12-30", "2027-01-05", 200),
        (2, "2026-12-31", "2027-01-06", 200),
        (2, "2027-01-01", "2027-01-07", 200),
        (2, "2027-01-02", "2027-01-08", 200),
        (2, "2027-01-03", "2027-01-09", 200),
        (2, "2026-12-30", "2027-01-05", 400),
        (2, "2026-12-01", "2026-12-29", 200),
    ]
)
async def test_booking(db, auth_ac, room_id, date_from, date_to, status_code):
    #room = (await db.rooms.get_all())[0]
    response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )
    result = response.json()
    assert response.status_code == status_code
    if status_code == 200:
        assert result["message"] == "Бронирование успешно создано"
        assert result["booking"]


@pytest.fixture(scope="session")
async def delete_all_bookings(db):
    await db.bookings.delete()
    await db.commit()


@pytest.mark.parametrize(
    "room_id, date_from, date_to, bookings_quantity",
    [
        (2, "2026-12-30", "2027-01-05", 1),
        (2, "2026-12-30", "2027-01-05", 2),
        (2, "2026-12-30", "2027-01-05", 3),
    ]
)
async def test_add_and_get_bookings(
        delete_all_bookings, db, auth_ac, room_id, date_from, date_to, bookings_quantity
):
    response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )
    assert response.status_code == 200
    my_bookings = (await auth_ac.get("/bookings/me")).json()
    assert len(my_bookings) == bookings_quantity