from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, insert, update
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """
    A base repository class for database operations.

    This class provides basic CRUD operations using SQLAlchemy's async session.
    It is intended to be subclassed by specific repository classes that define
    the model attribute to specify the SQLAlchemy model to operate on.

    Attributes:
        model: The SQLAlchemy model class associated with this repository.
        session: The SQLAlchemy async session used for database operations.

    Methods:
        get_all: Retrieves all records from the database for the associated model.
        get_one_or_none: Retrieves a single record based on filter criteria, or None if not found.
        add: Adds a new record to the database and returns the created instance.
    """

    model = None

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            result = result.scalars().one_or_none()
            if result is None:
                raise HTTPException(status_code=404, detail="Hotel not found")
            return result
        except MultipleResultsFound:
            raise HTTPException(status_code=400, detail="Multiple hotels found")

    async def add(self,  data: BaseModel) -> BaseModel:
        insert_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(insert_data_stmt)
        return result.scalar_one()

    async def edit(self, data: BaseModel, **filter_by) -> None:
        obj_for_edit = await self.get_one_or_none(**filter_by)
        update_stmt = update(self.model).where(self.model.id == obj_for_edit.id).values(**data.model_dump())
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by) -> None:
        hotel_for_delete = await self.get_one_or_none(**filter_by)
        await self.session.delete(hotel_for_delete)
