from fastapi import APIRouter, HTTPException, Body, Response
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import UserIdDep
from src.schemas.users import UserRequestAdd, UserAdd, UserLogin
from src.database import async_session_maker
from src.repositories.users import UserRepository
from src.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация и аутентификация"]
)


@router.post("/login")
async def login_user(
        data: UserLogin,
        response: Response
):
    async with async_session_maker() as session:
        user = await UserRepository(session).get_user_with_hashed_password(data.email)
        
        if not user:
            raise HTTPException(status_code=401, detail="Такой email не зарегистрирован")
        
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Неверный пароль")
        
        access_token = AuthService().create_access_token({
            "user_id": user.id
        })
        response.set_cookie(key="access_token", value=access_token)
        return {"access_token": access_token}


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
    hashed_password = AuthService().get_password_hash(password=user.password)
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
            raise HTTPException(status_code=400, detail="User with this email already exists")

    return {"message": "User registered successfully", "user": auth_user}


@router.get("/me")
async def get_me(
        user_id: UserIdDep
):
    async with async_session_maker() as session:
        user = await UserRepository(session).get_by_id(user_id)
    return {"user": user}


@router.post("/logout")
async def logout_user(
        response: Response
):
    response.delete_cookie("access_token")
    return {"message": "User logged out successfully"}
