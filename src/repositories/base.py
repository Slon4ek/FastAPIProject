from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_by_filter(self, *filter, **filter_by) -> list[BaseModel]:
        query = (
            select(self.model)
            .filter(*filter)
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return [self.schema.model_validate(item, from_attributes=True) for item in result.scalars().all()]

    async def get_all(self) -> list[BaseModel]:
        return await self.get_all_by_filter()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            result = result.scalars().one_or_none()
            if result is None:
                return None
            return self.schema.model_validate(result, from_attributes=True)
        except MultipleResultsFound:
            raise HTTPException(status_code=400, detail=f"Найдено более одного объекта по заданным параметрам")

    async def add(self, data: BaseModel) -> BaseModel:
        insert_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(insert_data_stmt)
        return self.schema.model_validate(result.scalar_one(), from_attributes=True)

    async def edit(self, data: BaseModel, for_patch: bool = False, **filter_by) -> None:
        for_edit = await self.get_one_or_none(**filter_by)
        if for_edit is None:
            raise HTTPException(status_code=404, detail=f"Not found")
        update_stmt = (
            update(self.model)
            .where(self.model.id == for_edit.id)
            .values(**data.model_dump(exclude_unset=for_patch))
        )
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by) -> None:
        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)
