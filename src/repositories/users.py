from pydantic.v1 import EmailStr
from sqlalchemy import select

from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.schemas.users import User, UserWithHashedPassword


class UserRepository(BaseRepository):
    model = UsersOrm
    name = "User"
    table_name = "users"
    schema = User

    async def get_user_with_hashed_password(self, email: EmailStr) -> UserWithHashedPassword | None:
        qwery = select(self.model).filter_by(email=email)
        result = await self.session.execute(qwery)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return UserWithHashedPassword.model_validate(model)
