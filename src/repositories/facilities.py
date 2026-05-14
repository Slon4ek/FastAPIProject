from psycopg.errors import ForeignKeyViolation
from sqlalchemy import select, delete, insert, exc

from src.exceptions import FacilityNotFoundException
from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FacilitiesDataMapper, RoomFacilitiesDataMapper


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilitiesDataMapper


class RoomFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesOrm
    mapper = RoomFacilitiesDataMapper

    async def set_room_facilities(self, room_id: int, facilities_ids: list[int]) -> None:
        query = select(self.model.facility_id).filter_by(room_id=room_id)
        res = await self.session.execute(query)
        current_facilities = res.scalars().all()
        ids_for_delete = list(set(current_facilities) - set(facilities_ids))
        ids_for_add = list(set(facilities_ids) - set(current_facilities))
        try:
            if ids_for_delete:
                room_facilities_delete_stmt = delete(self.model).filter(
                    self.model.room_id == room_id, self.model.facility_id.in_(ids_for_delete)
                )
                await self.session.execute(room_facilities_delete_stmt)

            if ids_for_add:
                room_facilities_insert_stmt = insert(self.model).values(
                    [{"room_id": room_id, "facility_id": f_id} for f_id in ids_for_add]
                )
                await self.session.execute(room_facilities_insert_stmt)
        except exc.IntegrityError as e:
            if isinstance(e.orig, ForeignKeyViolation):
                raise FacilityNotFoundException(e.orig.args[0]) from e
            else:
                raise e
