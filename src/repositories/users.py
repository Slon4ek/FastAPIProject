

from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.schemas.users import User


class UserRepository(BaseRepository):
    model = UsersOrm
    name = "User"
    table_name = "users"
    schema = User
