import pytest
from httpx import AsyncClient

from src.utils.db_manager import DBManager


@pytest.mark.parametrize(
    "date_from, date_to, status_code",
    [
        ("2026-06-01", "2026-06-10", 200),
        ("2026-06-01", "2026-06-01", 400),
        ("2026-06-01", "2026-05-01", 400),
    ],
)
async def test_get_hotels_rooms(
    ac: AsyncClient, db: DBManager, date_from: str, date_to: str, status_code: int
):
    hotel = (await db.hotels.get_all())[0]
    get_all_hotel_rooms_request = await ac.get(
        f"/hotels/{hotel.id}/rooms",
        params={
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert get_all_hotel_rooms_request.status_code == status_code


async def test_room_flow(
    ac: AsyncClient,
    db: DBManager,
) -> None:
    hotel = (await db.hotels.get_all())[0]
    create_room_request = await ac.post(
        f"/hotels/{hotel.id}/rooms",
        json={
            "title": "Test room",
            "description": "Test room description",
            "price": 1000,
            "quantity": 100,
            "facilities_ids": [1, 2, 3],
        },
    )
    assert create_room_request.status_code == 200
    assert create_room_request.json()
    room_response = create_room_request.json()
    assert room_response["message"] == "Room created"
    assert room_response["room"]
    room = room_response["room"]
    assert room["title"] == "Test room"

    put_room_request = await ac.put(
        f"/hotels/{room['hotel_id']}/rooms/{room['id']}",
        json={
            "title": "Стандартный номер",
            "description": "Стандартный номер 25 кв. м.",
            "price": 1000,
            "quantity": 100,
            "facilities_ids": [
                1,
            ],
        },
    )
    assert put_room_request.status_code == 200

    patch_room_request = await ac.patch(
        f"/hotels/{room['hotel_id']}/rooms/{room['id']}",
        json={
            "title": "Patched test room",
        },
    )
    assert patch_room_request.status_code == 200
    assert patch_room_request.json()["message"] == "Room updated"

    get_room_request = await ac.get(f"/hotels/{room['hotel_id']}/rooms/{room['id']}")
    assert get_room_request.status_code == 200
    assert get_room_request.json()["id"] == room["id"]
    assert get_room_request.json()["hotel_id"] == hotel.id
    assert get_room_request.json()["facilities"][0]["id"] == 1
    assert get_room_request.json()["title"] == "Patched test room"

    delete_room_request = await ac.delete(
        f"/hotels/{room['hotel_id']}/rooms/{room['id']}",
    )
    assert delete_room_request.status_code == 200
    assert delete_room_request.json()["message"] == "Room deleted"

    get_after_delete_request = await ac.get(f"/hotels/{room['hotel_id']}/rooms/{room['id']}")
    assert get_after_delete_request.status_code == 404
    assert get_after_delete_request.json()["detail"] == "Room not found"
