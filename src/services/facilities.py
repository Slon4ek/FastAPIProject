from typing import List

from src.exceptions import NotFoundError
from src.schemas.facility import FacilityAdd, Facility
from src.services.base import BaseService
from src.utils.db_manager import DBManager


class FacilitiesService(BaseService):
    db: DBManager

    async def add_facility(self, data: FacilityAdd):
        facility = await self.db.facilities.add(data)
        await self.db.commit()
        return facility


    async def get_all_facilities(self) -> List[Facility]:
        return await self.db.facilities.get_all()

    async def delete_facility(self, facility_id: int) -> None:
        result = await self.db.facilities.delete(id=facility_id)
        if not result.rowcount:
            raise NotFoundError
        await self.db.commit()