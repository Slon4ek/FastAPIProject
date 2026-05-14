from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from src.config import settings
from src.exceptions import (
    AuthenticationError,
    JWTExpiredError,
    JWTDecodeError,
    IsAlreadyExistsError,
    UserAlreadyExistsException,
)
from src.schemas.users import UserRequestAdd, User, UserAdd, UserLogin
from src.services.base import BaseService
from src.utils.db_manager import DBManager


class AuthService(BaseService):
    db: DBManager
    password_hash = PasswordHash.recommended()
    token_expiration = timedelta(minutes=30)
    token_algorithm = settings.JWT_ALGORITHM
    token_secret_key = settings.JWT_SECRET_KEY

    async def login(self, data: UserLogin):
        user = await self.db.users.get_user_with_hashed_password(data.email)
        if not user or not self.verify_password(data.password, user.hashed_password):
            raise AuthenticationError
        return self.create_access_token({"user_id": user.id})

    async def create_user(self, user: UserRequestAdd) -> User:
        hashed_password = self.get_password_hash(user.password)
        new_user = UserAdd(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            hashed_password=hashed_password,
        )
        try:
            auth_user = await self.db.users.add(new_user)
            await self.db.commit()
            return auth_user
        except IsAlreadyExistsError as exc:
            raise UserAlreadyExistsException(exc.args[0]) from exc

    async def get_user_info(self, user_id: int) -> User:
        return await self.db.users.get_one(id=user_id)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + self.token_expiration
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(to_encode, self.token_secret_key, algorithm=self.token_algorithm)
        return encoded_jwt

    def get_password_hash(self, password: str) -> str:
        return self.password_hash.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_hash.verify(plain_password, hashed_password)

    def decode_access_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.token_secret_key, algorithms=[self.token_algorithm])
        except jwt.ExpiredSignatureError:
            raise JWTExpiredError
        except jwt.exceptions.DecodeError:
            raise JWTDecodeError
