from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserRequestAdd(BaseModel):
    username: str = Field(examples=[
        "user1", "user2"
    ])
    email: EmailStr
    first_name: str | None = Field(None, description="Имя (Не обязательно)")
    last_name: str | None = Field(None, description="Фамилия (Не обязательно)")
    password: str


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
