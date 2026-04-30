import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "date_from, date_to, status_code",
    [
        ("2026-06-01", "2026-06-10", 200),
        ("2026-06-01", "2026-06-01", 400),
        ("2026-06-01", "2026-05-01", 400),
    ],
)
async def test_get_hotels(ac: AsyncClient, date_from: str, date_to: str, status_code: int):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert response.status_code == status_code
    assert response.json()


async def test_hotel_flow(ac: AsyncClient):
    # add new hotel
    new_hotel_request = await ac.post(
        "/hotels", json={"title": "test hotel", "stars": 5, "location": "test location"}
    )
    new_hotel = new_hotel_request.json()["data"]
    assert new_hotel_request.status_code == 200
    assert new_hotel["id"]

    # put added hotel
    put_hotel_request = await ac.put(
        "/hotels/{hotel_id}".format(hotel_id=new_hotel["id"]),
        json={"title": "put test hotel", "stars": 5, "location": "test location"},
    )
    assert put_hotel_request.status_code == 200

    # patch added hotel
    patch_hotel_request = await ac.patch(
        "/hotels/{hotel_id}".format(hotel_id=new_hotel["id"]),
        json={"location": "patch test location"},
    )
    assert patch_hotel_request.status_code == 200

    # get added hotel end check changes after put/patch
    get_hotel_request = await ac.get(
        "/hotels/{hotel_id}".format(hotel_id=new_hotel["id"]),
    )
    assert get_hotel_request.status_code == 200
    assert get_hotel_request.json()["id"] == new_hotel["id"]
    assert get_hotel_request.json()["title"] == "put test hotel"
    assert get_hotel_request.json()["location"] == "patch test location"

    # delete added hotel
    delete_hotel_request = await ac.delete(
        "/hotels/{hotel_id}".format(hotel_id=new_hotel["id"]),
    )
    assert delete_hotel_request.status_code == 200
