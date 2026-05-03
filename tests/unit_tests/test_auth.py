from src.services.auth import AuthService


def test_create_access_token(db):
    data = {"user_id": 1, "email": "test@test.com"}
    token = AuthService(db).create_access_token(data)

    assert token is not None
    assert isinstance(token, str)
