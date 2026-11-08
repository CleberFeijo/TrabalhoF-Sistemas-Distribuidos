from tests.conftest import Api


def test_public_register_returns_token_and_basic_role(api: Api):
    user = api.register(email="Nova@Example.com")
    assert user["user"]["roles"] == ["user"]
    assert user["user"]["email"] == "nova@example.com"
    assert user["user"]["plan"] == "free"
    assert "password_hash" not in user["user"]
    me = api.c.get("/v1/users/me", headers=user["headers"])
    assert me.status_code == 200


def test_duplicate_email_is_rejected_case_insensitively(api: Api):
    api.register(email="dup@example.com")
    r = api.c.post("/v1/auth/register", json={
        "name": "B", "last_name": "C", "email": "DUP@example.com", "password": "outra-senha-1",
    })
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "email_taken"


def test_register_validates_input(api: Api):
    r = api.c.post("/v1/auth/register", json={"name": "A", "last_name": "B", "email": "x@example.com",
                                              "password": "curta"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
    r = api.c.post("/v1/auth/register", json={"name": "A", "last_name": "B", "email": "x@example.com",
                                              "password": "senha-boa-1", "roles": ["admin"]})
    assert r.status_code == 422, "campos extras (ex.: roles) não podem ser aceitos no cadastro"


def test_bad_credentials_return_401_not_500(api: Api):
    api.register(email="ok@example.com", password="senha-certa-1")
    for username, password in [("ok@example.com", "errada-123"), ("ninguem@example.com", "qualquer-1")]:
        r = api.c.post("/v1/auth/login", data={"username": username, "password": password})
        assert r.status_code == 401
        assert r.json() == {"error": {"code": "invalid_credentials", "message": "Email ou senha incorretos."}}


def test_invalid_or_missing_token_returns_401_without_traceback(api: Api):
    for headers in [{}, {"Authorization": "Bearer lixo"}, {"Authorization": "Basic abc"}]:
        r = api.c.get("/v1/users/me", headers=headers)
        assert r.status_code == 401
        assert "traceback" not in r.text.lower()


def test_logout_revokes_existing_tokens(api: Api):
    user = api.register()
    assert api.c.post("/v1/auth/logout", headers=user["headers"]).status_code == 200
    r = api.c.get("/v1/users/me", headers=user["headers"])
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "session_revoked"


def test_change_password_rotates_token(api: Api):
    user = api.register(password="senha-antiga-1")
    r = api.c.post("/v1/users/me/password", headers=user["headers"],
                   json={"current_password": "errada", "new_password": "senha-nova-1"})
    assert r.status_code == 401
    r = api.c.post("/v1/users/me/password", headers=user["headers"],
                   json={"current_password": "senha-antiga-1", "new_password": "senha-nova-1"})
    assert r.status_code == 200
    new_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    assert api.c.get("/v1/users/me", headers=user["headers"]).status_code == 401
    assert api.c.get("/v1/users/me", headers=new_headers).status_code == 200
    email = user["user"]["email"]
    assert api.c.post("/v1/auth/login", data={"username": email, "password": "senha-antiga-1"}).status_code == 401
    api.login(email, "senha-nova-1")


def test_startup_is_idempotent(api: Api, raw_db):
    from fastapi.testclient import TestClient

    from app.main import create_app

    before = raw_db.users.count_documents({})
    with TestClient(create_app()):
        pass
    with TestClient(create_app()):
        pass
    assert raw_db.users.count_documents({}) == before == 1  # apenas o admin inicial
    assert raw_db.users.count_documents({"roles": "admin"}) == 1
