from pydantic import BaseModel, ConfigDict, Field


class FacilityAdd(BaseModel):
    title: str = Field(min_length=1)


class Facility(FacilityAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomFacilitiesAdd(BaseModel):
    room_id: int
    facility_id: int


class RoomFacilities(RoomFacilitiesAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)
