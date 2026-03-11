from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from pwdlib import PasswordHash

from src.config import settings


class AuthService:
    password_hash = PasswordHash.recommended()
    token_expiration = timedelta(minutes=30)
    token_algorithm = settings.JWT_ALGORITHM
    token_secret_key = settings.JWT_SECRET_KEY

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
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Invalid token")
