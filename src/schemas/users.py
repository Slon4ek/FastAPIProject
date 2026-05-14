from typing import Annotated

from pydantic import BaseModel, EmailStr, ConfigDict, Field, StringConstraints


class UserLogin(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]


class UserRequestAdd(UserLogin):
    username: str = Field(min_length=1)
    first_name: str | None = Field(None, min_length=1)
    last_name: str | None = Field(None, min_length=1)


class UserAdd(BaseModel):
    username: str
    email: EmailStr
    first_name: str | None = Field(None)
    last_name: str | None = Field(None)
    hashed_password: str


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str | None = Field(None)
    last_name: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)


class UserWithHashedPassword(User):
    hashed_password: str
