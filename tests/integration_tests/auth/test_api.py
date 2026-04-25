import pytest


@pytest.mark.parametrize(
    "email, password, username, first_name, last_name, status_code",
    [
        ("user1@example.ru", "12345678", "user1", "test", "test", 200),
        ("user1@example.ru", "12345678", "user2", "test", "test", 409),
        ("user2@example.ru", "", "user3", "test", "test", 422),
        ("user2@example", "qwerty1234", "user4", "test", "test", 422),
    ],
)
async def test_auth_flow(ac, email, password, username, first_name, last_name, status_code):
    # /register
    request = await ac.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    assert request.status_code == status_code
    if status_code == 409:
        assert request.json() == {"detail": "User with this email already exists"}
        return
    elif status_code == 422:
        return

    user = request.json()["user"]
    assert user["id"]
    assert user["email"] == email

    # /login
    login_request = await ac.post("/auth/login", json={"email": email, "password": password})
    assert login_request.status_code == 200
    assert ac.cookies["access_token"]
    assert "access_token" in login_request.json()

    # /me
    me_request = await ac.get("auth/me")
    assert me_request.status_code == 200
    user_info = me_request.json()["user"]
    assert user_info["id"] == user["id"]
    assert user_info["username"] == username
    assert user_info["email"] == email
    assert user_info["first_name"] == first_name
    assert user_info["last_name"] == last_name
    assert "password" not in user_info
    assert "hashed_password" not in user_info

    # /logout
    logout_request = await ac.post("auth/logout")
    assert logout_request.status_code == 200
    assert ac.cookies.get("access_token") is None
    assert logout_request.json() == {"message": "User logged out successfully"}
