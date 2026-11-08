from tests.conftest import BASE_LAT, BASE_LON, Api, offset


def _nearby(api: Api, headers, lat=BASE_LAT, lon=BASE_LON, **params):
    r = api.c.get("/v1/landmarks/nearby", headers=headers, params={"lat": lat, "lon": lon, **params})
    assert r.status_code == 200, r.text
    return r.json()


def test_nearby_returns_only_approved_within_radius_sorted_by_distance(api: Api):
    user = api.register()
    near = api.landmark(lat=offset(BASE_LAT, BASE_LON, north_m=150)[0], name="Perto")
    nearest = api.landmark(name="Aqui")
    api.landmark(lat=offset(BASE_LAT, BASE_LON, north_m=500)[0], name="Longe")
    api.landmark(name="Pendente", status="pending")
    api.landmark(name="Rejeitado", status="rejected")

    result = _nearby(api, user["headers"])
    assert [x["id"] for x in result] == [nearest, near]
    assert result[0]["distance_m"] < 1 and 140 < result[1]["distance_m"] < 160
    assert all(x["chat_available"] for x in result)

    wide = _nearby(api, user["headers"], radius=1000)
    assert [x["name"] for x in wide] == ["Aqui", "Perto", "Longe"]
    assert wide[2]["chat_available"] is False


def test_nearby_counts_only_approved_curiosities(api: Api):
    user = api.register()
    lid = api.landmark()
    api.curiosity(lid)
    api.curiosity(lid)
    api.curiosity(lid, status="pending")
    assert _nearby(api, user["headers"])[0]["curiosity_count"] == 2


def test_nearby_validates_coordinates_and_requires_auth(api: Api):
    user = api.register()
    assert api.c.get("/v1/landmarks/nearby", params={"lat": 0, "lon": 0}).status_code == 401
    for params in [{"lat": "abc", "lon": 0}, {"lat": 95, "lon": 0}, {"lat": 0}]:
        assert api.c.get("/v1/landmarks/nearby", headers=user["headers"], params=params).status_code == 422


def test_user_suggestion_is_pending_until_moderated(api: Api):
    author = api.register()
    other = api.register()
    mod = api.moderator()
    r = api.c.post("/v1/landmarks", headers=author["headers"], json={
        "name": "Igreja Nova", "latitude": BASE_LAT, "longitude": BASE_LON,
        "curiosity": "Foi construída em pedra trazida de longe.",
    })
    assert r.status_code == 201
    lid = r.json()["id"]
    assert r.json()["status"] == "pending" and r.json()["created_by"] == author["user"]["id"]

    assert _nearby(api, other["headers"]) == []
    assert api.c.get(f"/v1/landmarks/{lid}", headers=other["headers"]).status_code == 404
    assert api.c.get(f"/v1/landmarks/{lid}", headers=author["headers"]).status_code == 200
    mine = api.c.get("/v1/users/me/landmarks", headers=author["headers"]).json()
    assert mine["total"] == 1

    r = api.c.post(f"/v1/moderation/landmarks/{lid}/approve", headers=mod["headers"])
    assert r.status_code == 200 and r.json()["status"] == "approved"
    found = _nearby(api, other["headers"])
    assert [x["id"] for x in found] == [lid]
    # a curiosidade inicial segue pendente até ser moderada separadamente
    assert found[0]["curiosity_count"] == 0


def test_moderator_creates_landmark_already_approved(api: Api):
    mod = api.moderator()
    r = api.c.post("/v1/landmarks", headers=mod["headers"], json={
        "name": "Farol", "latitude": BASE_LAT, "longitude": BASE_LON, "image_url": "https://example.org/farol.jpg",
    })
    assert r.status_code == 201 and r.json()["status"] == "approved"


def test_curiosities_show_their_own_authors(api: Api):
    """Regressão: antes todas as curiosidades apareciam com o nome de quem postou por último."""
    ana = api.register(name="Ana")
    bia = api.register(name="Bia")
    lid = api.landmark()
    api.curiosity(lid, text="Curiosidade escrita pela Ana.", author_id=ana["user"]["id"])
    api.curiosity(lid, text="Curiosidade importada da Wikipédia.",
                  source={"name": "wikipedia", "url": "https://pt.wikipedia.org/wiki/X", "license": "CC BY-SA 4.0"})
    r = api.c.post(f"/v1/landmarks/{lid}/curiosities", headers=bia["headers"],
                   json={"text": "Curiosidade escrita pela Bia."})
    assert r.status_code == 201 and r.json()["status"] == "pending"
    assert r.json()["author"]["id"] == bia["user"]["id"]

    items = api.c.get(f"/v1/landmarks/{lid}/curiosities", headers=bia["headers"]).json()["items"]
    by_text = {i["text"]: i for i in items}
    assert set(by_text) == {"Curiosidade escrita pela Ana.", "Curiosidade importada da Wikipédia."}
    assert by_text["Curiosidade escrita pela Ana."]["author"]["name"] == "Ana Teste"
    imported = by_text["Curiosidade importada da Wikipédia."]
    assert imported["author"] is None and imported["source"]["name"] == "wikipedia"


def test_curiosity_author_cannot_be_spoofed(api: Api):
    user = api.register()
    lid = api.landmark()
    r = api.c.post(f"/v1/landmarks/{lid}/curiosities", headers=user["headers"],
                   json={"text": "Texto suficientemente longo.", "email": "outra@pessoa.com"})
    assert r.status_code == 422


def test_cannot_post_curiosity_on_hidden_or_missing_landmark(api: Api):
    user = api.register()
    pending = api.landmark(status="pending")
    for lid in [pending, "000000000000000000000000", "invalido"]:
        r = api.c.post(f"/v1/landmarks/{lid}/curiosities", headers=user["headers"], json={"text": "Texto longo o bastante."})
        assert r.status_code == 404


def test_delete_curiosity_permissions(api: Api, raw_db):
    author = api.register()
    other = api.register()
    mod = api.moderator()
    lid = api.landmark()
    c1 = api.curiosity(lid, author_id=author["user"]["id"])
    c2 = api.curiosity(lid, author_id=author["user"]["id"])
    assert api.c.delete(f"/v1/curiosities/{c1}").status_code == 401
    assert api.c.delete(f"/v1/curiosities/{c1}", headers=other["headers"]).status_code == 403
    assert api.c.delete(f"/v1/curiosities/{c1}", headers=author["headers"]).status_code == 204
    assert api.c.delete(f"/v1/curiosities/{c2}", headers=mod["headers"]).status_code == 204
    assert raw_db.curiosities.count_documents({}) == 0


def test_delete_landmark_permissions_and_cascade(api: Api, raw_db):
    admin = api.admin()
    user = api.register()
    lid = api.landmark()
    api.curiosity(lid)
    assert api.c.delete(f"/v1/landmarks/{lid}").status_code == 401
    assert api.c.delete(f"/v1/landmarks/{lid}", headers=user["headers"]).status_code == 403
    assert api.c.delete(f"/v1/landmarks/{lid}", headers=admin["headers"]).status_code == 204
    assert raw_db.curiosities.count_documents({}) == 0

    r = api.c.post("/v1/landmarks", headers=user["headers"],
                   json={"name": "Minha sugestão", "latitude": 0, "longitude": 0})
    assert api.c.delete(f"/v1/landmarks/{r.json()['id']}", headers=user["headers"]).status_code == 204


def test_moderator_can_edit_landmark(api: Api):
    mod = api.moderator()
    user = api.register()
    lid = api.landmark()
    assert api.c.patch(f"/v1/landmarks/{lid}", headers=user["headers"], json={"name": "X"}).status_code == 403
    r = api.c.patch(f"/v1/landmarks/{lid}", headers=mod["headers"], json={"name": "Nome corrigido", "latitude": -22.6})
    assert r.status_code == 200
    assert r.json()["name"] == "Nome corrigido" and r.json()["latitude"] == -22.6
    assert r.json()["longitude"] == BASE_LON


def test_patch_cannot_null_required_fields(api: Api):
    mod = api.moderator()
    lid = api.landmark(name="Original")
    r = api.c.patch(f"/v1/landmarks/{lid}", headers=mod["headers"], json={"name": None, "latitude": None})
    assert r.status_code == 200 and r.json()["name"] == "Original" and r.json()["latitude"] == BASE_LAT
