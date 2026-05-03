from fastapi import APIRouter, HTTPException, Body, Response
from fastapi.openapi.models import Example

from src.exceptions import AuthenticationError, UserAlreadyExistsException, \
    EmailAlreadyExistsHTTPException, UsernameAlreadyExistsHTTPException
from src.api.dependencies import UserIdDep, DBDep
from src.schemas.users import UserRequestAdd, UserLogin
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post(
    "/login",
    summary="Аутентификация пользователя",
    description="Аутентификация пользователя по логину(email) и паролю, "
    "генерирует токен доступа и устанавливает его в куки",
)
async def login_user(db: DBDep, data: UserLogin, response: Response):
    try:
        access_token = await AuthService(db).login(data)
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    response.set_cookie(key="access_token", value=access_token)
    return {"access_token": access_token}


@router.post(
    "/register",
    summary="Регистрация пользователя",
    description="Регистрация нового пользователя. first_name, last_name - не обязательные поля",
)
async def register_user(
    db: DBDep,
    user: UserRequestAdd = Body(
        openapi_examples={
            "John Doe": Example(
                value={
                    "username": "user1",
                    "email": "user1@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "password": "password123",
                }
            ),
            "Anna Smith": Example(
                value={
                    "username": "admin",
                    "email": "admin@example.com",
                    "first_name": "Anna",
                    "last_name": "Smith",
                    "password": "qwerty123",
                }
            ),
        }
    ),
):
    try:
        auth_user = await AuthService(db).create_user(user)
    except UserAlreadyExistsException as e:
        if "email" in e.detail:
            raise EmailAlreadyExistsHTTPException from e
        elif "username" in e.detail:
            raise UsernameAlreadyExistsHTTPException from e
        else:
            raise e

    return {"message": "User registered successfully", "user": auth_user}


@router.get(
    "/me",
    summary="Получить информацию о текущем пользователе",
    description="Получение информации о текущем пользователе по токену доступа",
)
async def get_me(db: DBDep, user_id: UserIdDep):
    return await AuthService(db).get_user_info(user_id)


@router.post("/logout", summary="Выйти из системы", description="Удаление токена доступа из куки")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"message": "User logged out successfully"}
