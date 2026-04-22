async def test_booking(db, auth_ac):
    room = (await db.rooms.get_all())[0]
    hotel_id = room.hotel_id
    response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": room.id,
            "hotel_id": hotel_id,
            "date_from": "2026-12-30",
            "date_to": "2027-01-05",
        }
    )
    result = response.json()
    assert response.status_code == 200
    assert result["message"] == "Бронирование успешно создано"
    assert result["booking"]