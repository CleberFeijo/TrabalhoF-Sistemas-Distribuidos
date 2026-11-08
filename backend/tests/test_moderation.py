from tests.conftest import Api


def test_queue_requires_moderator(api: Api):
    user = api.register()
    assert api.c.get("/v1/moderation/curiosities", headers=user["headers"]).status_code == 403
    assert api.c.get("/v1/moderation/landmarks", headers=user["headers"]).status_code == 403


def test_approve_and_reject_curiosities(api: Api):
    author = api.register()
    mod = api.moderator()
    lid = api.landmark()
    first = api.c.post(f"/v1/landmarks/{lid}/curiosities", headers=author["headers"],
                       json={"text": "Primeira curiosidade enviada."}).json()["id"]
    second = api.c.post(f"/v1/landmarks/{lid}/curiosities", headers=author["headers"],
                        json={"text": "Segunda curiosidade enviada."}).json()["id"]

    queue = api.c.get("/v1/moderation/curiosities", headers=mod["headers"]).json()
    assert [i["id"] for i in queue["items"]] == [first, second], "fila em ordem de chegada"
    assert queue["items"][0]["landmark_name"] == "Marco Teste"

    assert api.c.post(f"/v1/moderation/curiosities/{first}/approve", headers=mod["headers"]).json()["status"] == "approved"
    assert api.c.post(f"/v1/moderation/curiosities/{second}/reject", headers=mod["headers"], json={}).status_code == 422
    r = api.c.post(f"/v1/moderation/curiosities/{second}/reject", headers=mod["headers"],
                   json={"reason": "Sem fonte verificável."})
    assert r.json()["status"] == "rejected" and r.json()["rejection_reason"] == "Sem fonte verificável."

    public = api.c.get(f"/v1/landmarks/{lid}/curiosities", headers=author["headers"]).json()
    assert [i["id"] for i in public["items"]] == [first]
    mine = api.c.get("/v1/users/me/curiosities", headers=author["headers"], params={"status": "rejected"}).json()
    assert mine["items"][0]["rejection_reason"] == "Sem fonte verificável."
    assert api.c.get(f"/v1/moderation/curiosities/{first}/approve", headers=mod["headers"]).status_code == 405


def test_rejected_curiosity_hidden_from_others(api: Api):
    author = api.register()
    other = api.register()
    lid = api.landmark()
    cid = api.curiosity(lid, author_id=author["user"]["id"], status="rejected")
    assert api.c.get(f"/v1/curiosities/{cid}", headers=other["headers"]).status_code == 404
    assert api.c.get(f"/v1/curiosities/{cid}", headers=author["headers"]).status_code == 200


def test_moderation_of_missing_items(api: Api):
    mod = api.moderator()
    for path in ["landmarks", "curiosities"]:
        assert api.c.post(f"/v1/moderation/{path}/000000000000000000000000/approve",
                          headers=mod["headers"]).status_code == 404
        assert api.c.post(f"/v1/moderation/{path}/xyz/approve", headers=mod["headers"]).status_code == 404
