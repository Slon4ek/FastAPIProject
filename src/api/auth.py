from fastapi import APIRouter, HTTPException, Body
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError

from src.schemas.users import UserRequestAdd, UserAdd, User
from src.database import async_session_maker
from src.repositories.users import UserRepository

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация и аутентификация"]
)

password_hash = PasswordHash.recommended()

@router.post("/register")
async def register_user(
        user: UserRequestAdd = Body(
            openapi_examples={
                "user1": {
                    "summary": "User 1",
                    "value": {
                        "username": "user1",
                        "email": "user1@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "password": "password123"
                    }
                },
                "user2": {
                    "summary": "Admin",
                    "value": {
                        "username": "admin",
                        "email": "admin@example.com",
                        "first_name": "John",
                        "last_name": "Smith",
                        "password": "qwerty123"
                    }
                }
            }
        )
):
    hashed_password = password_hash.hash(password=user.password)
    new_user = UserAdd(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password
    )
    async with async_session_maker() as session:
        try:
            auth_user = await UserRepository(session).add(new_user)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=400, detail="User already exists")

    return {"message": "User registered successfully", "user": auth_user}
