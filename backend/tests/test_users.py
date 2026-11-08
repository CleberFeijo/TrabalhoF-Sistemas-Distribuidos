from tests.conftest import Api


def test_regular_user_cannot_manage_other_users(api: Api):
    attacker = api.register()
    victim = api.register()
    vid = victim["user"]["id"]
    h = attacker["headers"]
    assert api.c.get("/v1/users", headers=h).status_code == 403
    assert api.c.get(f"/v1/users/{vid}", headers=h).status_code == 403
    assert api.c.patch(f"/v1/users/{vid}", headers=h, json={"roles": ["user"]}).status_code == 403
    assert api.c.patch(f"/v1/users/{attacker['user']['id']}", headers=h, json={"roles": ["admin"]}).status_code == 403
    assert api.c.delete(f"/v1/users/{vid}", headers=h).status_code == 403
    # /me não aceita alteração de papéis
    assert api.c.patch("/v1/users/me", headers=h, json={"roles": ["admin"]}).status_code == 422


def test_admin_promotes_user_and_old_token_is_revoked(api: Api):
    admin = api.admin()
    user = api.register()
    uid = user["user"]["id"]
    r = api.c.patch(f"/v1/users/{uid}", headers=admin["headers"], json={"roles": ["moderator"]})
    assert r.status_code == 200
    assert r.json()["roles"] == ["moderator", "user"]
    assert api.c.get("/v1/users/me", headers=user["headers"]).status_code == 401
    fresh = api.login(user["user"]["email"], user["password"])
    assert api.c.get("/v1/moderation/curiosities", headers=fresh["headers"]).status_code == 200


def test_get_user_by_id_works_for_admin(api: Api):
    admin = api.admin()
    user = api.register()
    r = api.c.get(f"/v1/users/{user['user']['id']}", headers=admin["headers"])
    assert r.status_code == 200 and r.json()["email"] == user["user"]["email"]
    assert api.c.get("/v1/users/naoehumid", headers=admin["headers"]).status_code == 404
    assert api.c.get("/v1/users/000000000000000000000000", headers=admin["headers"]).status_code == 404


def test_last_admin_cannot_be_removed(api: Api):
    admin = api.admin()
    aid = admin["user"]["id"]
    r = api.c.patch(f"/v1/users/{aid}", headers=admin["headers"], json={"roles": ["user"]})
    assert r.status_code == 409


def test_update_me_and_email_change_requires_password(api: Api):
    user = api.register()
    h = user["headers"]
    r = api.c.patch("/v1/users/me", headers=h, json={"name": "Novo Nome"})
    assert r.status_code == 200 and r.json()["name"] == "Novo Nome"
    r = api.c.patch("/v1/users/me", headers=h, json={"email": "novo@example.com"})
    assert r.status_code == 401
    r = api.c.patch("/v1/users/me", headers=h, json={"email": "novo@example.com", "current_password": user["password"]})
    assert r.status_code == 200 and r.json()["email"] == "novo@example.com"
    other = api.register()
    r = api.c.patch("/v1/users/me", headers=other["headers"],
                    json={"email": "NOVO@example.com", "current_password": other["password"]})
    assert r.status_code == 409


def test_delete_account_keeps_approved_content_anonymously(api: Api, raw_db):
    user = api.register()
    uid = user["user"]["id"]
    lid = api.landmark()
    approved = api.curiosity(lid, author_id=uid, status="approved")
    api.curiosity(lid, author_id=uid, status="pending")
    assert api.c.request("DELETE", "/v1/users/me", headers=user["headers"], json={"password": "errada"}).status_code == 401
    r = api.c.request("DELETE", "/v1/users/me", headers=user["headers"], json={"password": user["password"]})
    assert r.status_code == 204
    assert raw_db.users.count_documents({"email": user["user"]["email"]}) == 0
    remaining = list(raw_db.curiosities.find({}))
    assert [str(d["_id"]) for d in remaining] == [approved]
    assert remaining[0]["author_id"] is None
    viewer = api.register()
    items = api.c.get(f"/v1/landmarks/{lid}/curiosities", headers=viewer["headers"]).json()["items"]
    assert items[0]["author"] is None


def test_admin_sets_plan_and_deactivates_user(api: Api):
    admin = api.admin()
    user = api.register()
    uid = user["user"]["id"]
    r = api.c.patch(f"/v1/users/{uid}", headers=admin["headers"], json={"plan": "premium"})
    assert r.status_code == 200 and r.json()["plan"] == "premium"
    assert api.c.get("/v1/users/me", headers=user["headers"]).status_code == 200, "trocar plano não derruba a sessão"
    r = api.c.patch(f"/v1/users/{uid}", headers=admin["headers"], json={"is_active": False})
    assert r.status_code == 200 and r.json()["is_active"] is False
    assert api.c.get("/v1/users/me", headers=user["headers"]).status_code == 401
    r = api.c.post("/v1/auth/login", data={"username": user["user"]["email"], "password": user["password"]})
    assert r.status_code == 401
    listed = api.c.get("/v1/users", headers=admin["headers"], params={"q": user["user"]["email"][:6]}).json()
    assert listed["total"] == 1
