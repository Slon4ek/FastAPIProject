from pydantic import BaseModel, ConfigDict


class FacilityAdd(BaseModel):
    title: str


class Facilities(FacilityAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomFacilitiesAdd(BaseModel):
    room_id: int
    facility_id: int


class RoomFacilities(RoomFacilitiesAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)