from src.services.auth import AuthService


def test_encode_and_decode_access_token():
    data = {"user_id": 1, "email": "test@test.com"}
    token = AuthService().create_access_token(data)
    pyload = AuthService().decode_access_token(token)

    assert pyload is not None
    assert pyload["user_id"] == data["user_id"]
