from typing import TypeVar, Generic, Type
from pydantic import BaseModel
from src.database import BaseModel as Base

DBModelType = TypeVar("DBModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class DataMapper(Generic[DBModelType, SchemaType]):
    db_model: Type[DBModelType]
    schema: Type[SchemaType]

    def map_to_domain_entity(self, data: DBModelType) -> SchemaType:
        return self.schema.model_validate(data, from_attributes=True)

    def map_to_persistence_entity(self, data: SchemaType) -> DBModelType:
        return self.db_model(**data.model_dump())
