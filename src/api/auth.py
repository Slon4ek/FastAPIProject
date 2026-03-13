from fastapi import APIRouter, HTTPException, Body, Response
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import UserIdDep, DBDep
from src.schemas.users import UserRequestAdd, UserAdd, UserLogin
from src.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация и аутентификация"]
)


@router.post(
    "/login",
    summary="Аутентификация пользователя",
    description="Аутентификация пользователя по логину(email) и паролю, "
                "генерирует токен доступа и устанавливает его в куки"
)
async def login_user(
        db: DBDep,
        data: UserLogin,
        response: Response
):
    user = await db.users.get_user_with_hashed_password(data.email)
        
    if not user or not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    access_token = AuthService().create_access_token({
        "user_id": user.id
    })
    response.set_cookie(key="access_token", value=access_token)
    return {"access_token": access_token}


@router.post(
    "/register",
    summary="Регистрация пользователя",
    description="Регистрация нового пользователя. first_name, last_name - не обязательные поля"
)
async def register_user(
        db: DBDep,
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
    try:
        auth_user = await db.users.add(new_user)
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    return {"message": "User registered successfully", "user": auth_user}


@router.get(
    "/me",
    summary="Получить информацию о текущем пользователе",
    description="Получение информации о текущем пользователе по токену доступа"
)
async def get_me(
        db: DBDep,
        user_id: UserIdDep
):
    user = await db.users.get_one_or_none(id=user_id)
    return {"user": user}


@router.post(
    "/logout",
    summary="Выйти из системы",
    description="Удаление токена доступа из куки"
)
async def logout_user(
        response: Response
):
    response.delete_cookie("access_token")
    return {"message": "User logged out successfully"}
