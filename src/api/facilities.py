from fastapi import APIRouter
from fastapi_cache.decorator import cache
from fastapi.exceptions import HTTPException

from src.api.dependencies import DBDep
from src.exceptions import NotFoundError
from src.schemas.facility import FacilityAdd
from src.services.facilities import FacilitiesService

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("", summary="Удобства в номерах", description="Получить список всех удобств")
@cache(expire=360)
async def get_facilities(db: DBDep):
    return await FacilitiesService(db).get_all_facilities()


@router.post("", summary="Добавить удобства")
async def add_facilities(db: DBDep, data: FacilityAdd):
    facility = await FacilitiesService(db).add_facility(data)
    return {"status": "Ok", "facility": facility}


@router.delete("/{facility_id}", summary="Удалить удобство")
async def delete_hotel(facility_id: int, db: DBDep):
    try:
        await FacilitiesService(db).delete_facility(facility_id)
        return {"message": "Deleted facility successfully"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Facility not found")
