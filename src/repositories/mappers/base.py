from typing import TypeVar, Generic
from pydantic import BaseModel
from src.database import BaseModel as Base

DBModelType = TypeVar("DBModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class DataMapper(Generic[DBModelType, SchemaType]):
    db_model: type[DBModelType]
    schema: type[SchemaType]

    def map_to_domain_entity(self, data):
        return self.schema.model_validate(data, from_attributes=True)

    def map_to_persistence_entity(self, data):
        return self.db_model(**data.model_dump())
