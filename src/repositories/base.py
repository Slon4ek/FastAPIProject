import re
from typing import Sequence, TypeVar, Any, Generic

from pydantic import BaseModel
from psycopg.errors import UniqueViolation, SyntaxError, ForeignKeyViolation
from sqlalchemy import select, insert, update, delete, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound, IntegrityError, ProgrammingError

from src.exceptions import (
    NotFoundError,
    IsAlreadyExistsError,
    EmptyDataException,
    RelationshipError,
)
from src.repositories.mappers.base import DataMapper
from src.database import BaseModel as BaseOrm

DBModelType = TypeVar("DBModelType", bound=BaseOrm)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
MapperType = TypeVar("MapperType", bound=DataMapper[Any, Any])


class BaseRepository(Generic[DBModelType, SchemaType, MapperType]):
    model: type[DBModelType]
    mapper: type[MapperType]
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_by_filter(self, *filter: Any, **filter_by: Any) -> list[SchemaType]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.mapper().map_to_domain_entity(item) for item in result.scalars().all()]

    async def get_all(self) -> list[SchemaType]:
        return await self.get_all_by_filter()

    async def get_one_or_none(
        self,
        with_relations: bool = False,
        relations_name: str | list[str] | None = None,
        **filter_by: Any,
    ) -> SchemaType | None:
        query = select(self.model).filter_by(**filter_by)

        if with_relations and relations_name:
            query = query.options(
                *[selectinload(getattr(self.model, name)) for name in relations_name]
            )

        result = (await self.session.execute(query)).scalars().one_or_none()
        if result is None:
            return None
        return self.mapper().map_to_domain_entity(result)

    async def get_one(
        self,
        with_relations: bool = False,
        relations_name: list[str] | None = None,
        **filter_by: Any,
    ) -> SchemaType:
        query = select(self.model).filter_by(**filter_by)

        if with_relations and relations_name:
            query = query.options(
                *[selectinload(getattr(self.model, name)) for name in relations_name]
            )
        try:
            result = (await self.session.execute(query)).scalar_one()
        except NoResultFound:
            raise NotFoundError
        return self.mapper().map_to_domain_entity(result)

    async def add(self, data: SchemaType) -> SchemaType | None:
        insert_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(insert_data_stmt)
            return self.mapper().map_to_domain_entity(result.scalar_one())
        except IntegrityError as exc:
            if isinstance(exc.orig, UniqueViolation):
                detail = re.findall(r"\((.*?)\)", exc.args[0].split("DETAIL: ")[-1])
                raise IsAlreadyExistsError(detail) from exc
            elif isinstance(exc.orig, ForeignKeyViolation):
                raise RelationshipError() from exc
            else:
                raise exc

    async def add_bulk(self, data: Sequence[SchemaType]) -> None:
        insert_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        try:
            await self.session.execute(insert_data_stmt)
        except IntegrityError as exc:
            if isinstance(exc.orig, UniqueViolation):
                detail = re.findall(r"\((.*?)\)", exc.args[0].split("DETAIL: ")[-1])
                raise IsAlreadyExistsError(detail) from exc
            elif isinstance(exc.orig, ForeignKeyViolation):
                raise RelationshipError() from exc
            else:
                raise exc

    async def edit(
        self, data: SchemaType, exclude_unset: bool = False, **filter_by: Any
    ) -> Result[Any]:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        try:
            return await self.session.execute(update_stmt)
        except ProgrammingError as exc:
            if isinstance(exc.orig, SyntaxError):
                raise EmptyDataException() from exc
            else:
                raise exc
        except IntegrityError as exc:
            if isinstance(exc.orig, UniqueViolation):
                detail = re.findall(r"\((.*?)\)", exc.args[0].split("DETAIL: ")[-1])
                raise IsAlreadyExistsError(detail) from exc
            elif isinstance(exc.orig, ForeignKeyViolation):
                raise RelationshipError() from exc
            else:
                raise exc

    async def delete(self, **filter_by: Any) -> Result[Any]:
        stmt = delete(self.model).filter_by(**filter_by)
        return await self.session.execute(stmt)
