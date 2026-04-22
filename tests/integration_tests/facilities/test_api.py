from src.schemas.facility import FacilityAdd


async def test_facility_add(ac):
    new_facility = FacilityAdd(
        title="Test Facility",
    )
    request = await ac.post(
        "/facilities",
        json=new_facility.model_dump()
    )
    assert request.status_code == 200
    assert request.json()["facility"]
    assert request.json()["facility"]["title"] == new_facility.title

async def test_get_facilities(ac):
    request = await ac.get("/facilities")
    assert request.status_code == 200
    assert isinstance(request.json(), list)
