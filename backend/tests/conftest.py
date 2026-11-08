"""Fixtures dos testes.

Os testes usam MongoDB de verdade (as consultas geográficas não funcionam em
mocks). Configure MONGO_URI (padrão: mongodb://localhost:27017) e, para os
testes de Redis, REDIS_URL. Cada execução usa um banco descartável.
"""
import os
import uuid

import pytest
from bson import ObjectId
from pymongo import MongoClient

os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ["MONGO_DB"] = f"hist_test_{uuid.uuid4().hex[:8]}"
os.environ["ENV"] = "test"
os.environ["JWT_SECRET"] = "test-secret-" + "x" * 40
os.environ["ADMIN_EMAIL"] = "admin@example.com"
os.environ["ADMIN_PASSWORD"] = "admin-password"
os.environ["CHAT_RATE_LIMIT_MESSAGES"] = "5"
os.environ.pop("REDIS_URL", None)
os.environ.pop("CHAT_PERSISTENCE_ENABLED", None)

from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.repositories.common import geo_point, utcnow  # noqa: E402

# Praça usada como referência nos testes (coordenadas arbitrárias em Rio das Ostras).
BASE_LAT, BASE_LON = -22.5031633, -41.9237467


def offset(lat: float, lon: float, north_m: float = 0, east_m: float = 0) -> tuple[float, float]:
    """Desloca uma coordenada alguns metros (aproximação suficiente para testes)."""
    import math

    return (
        lat + north_m / 111_320,
        lon + east_m / (111_320 * math.cos(math.radians(lat))),
    )


@pytest.fixture(scope="session")
def raw_db():
    client = MongoClient(os.environ["MONGO_URI"], tz_aware=True)
    db = client[os.environ["MONGO_DB"]]
    yield db
    client.drop_database(os.environ["MONGO_DB"])
    client.close()


@pytest.fixture
def settings_env(monkeypatch):
    """Permite alterar variáveis de ambiente antes de subir o app."""

    def apply(**values):
        for key, value in values.items():
            monkeypatch.setenv(key, str(value))
        get_settings.cache_clear()

    yield apply
    get_settings.cache_clear()


@pytest.fixture
def client(raw_db):
    for name in raw_db.list_collection_names():
        raw_db[name].delete_many({})
    get_settings.cache_clear()
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c
    get_settings.cache_clear()


class Api:
    """Atalhos para os testes."""

    def __init__(self, client: TestClient, db):
        self.c = client
        self.db = db

    def register(self, email: str | None = None, password: str = "senha-forte-1", name: str = "Ana") -> dict:
        email = email or f"{uuid.uuid4().hex[:8]}@example.com"
        r = self.c.post("/v1/auth/register", json={
            "name": name, "last_name": "Teste", "email": email, "password": password,
        })
        assert r.status_code == 201, r.text
        data = r.json()
        data["headers"] = {"Authorization": f"Bearer {data['access_token']}"}
        data["password"] = password
        return data

    def login(self, email: str, password: str) -> dict:
        r = self.c.post("/v1/auth/login", data={"username": email, "password": password})
        assert r.status_code == 200, r.text
        data = r.json()
        data["headers"] = {"Authorization": f"Bearer {data['access_token']}"}
        return data

    def admin(self) -> dict:
        return self.login("admin@example.com", "admin-password")

    def moderator(self) -> dict:
        user = self.register(name="Moderador")
        self.db.users.update_one({"_id": ObjectId(user["user"]["id"])}, {"$set": {"roles": ["user", "moderator"]}})
        return user  # o token continua válido: alteração direta no banco não incrementa token_version

    def landmark(self, *, lat=BASE_LAT, lon=BASE_LON, status="approved", name="Marco Teste",
                 created_by=None, source=None) -> str:
        now = utcnow()
        result = self.db.landmarks.insert_one({
            "name": name, "description": "Descrição", "location": geo_point(lat, lon),
            "country": "BR", "status": status, "created_by": created_by, "source": source,
            "created_at": now, "updated_at": now,
        })
        return str(result.inserted_id)

    def curiosity(self, landmark_id: str, *, text="Uma curiosidade qualquer.", author_id=None,
                  status="approved", source=None) -> str:
        now = utcnow()
        result = self.db.curiosities.insert_one({
            "landmark_id": ObjectId(landmark_id), "text": text,
            "author_id": ObjectId(author_id) if author_id else None,
            "source": source, "status": status, "created_at": now, "updated_at": now,
        })
        return str(result.inserted_id)


@pytest.fixture
def api(client, raw_db) -> Api:
    return Api(client, raw_db)
