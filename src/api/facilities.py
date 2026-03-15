from fastapi import APIRouter

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd

router = APIRouter(
    prefix="/facilities",
    tags=["Удобства"]
)


@router.get("", summary="Удобства в номерах", description="Получить список всех удобств")
async def get_facilities(
        db: DBDep
):
    return await db.facilities.get_all()

@router.post("", summary="Добавить удобства")
async def add_facilities(
        db: DBDep,
        data: FacilityAdd
):
    facility = await db.facilities.add(data)
    await db.commit()
    return {"status": "Ok", "facility": facility}
