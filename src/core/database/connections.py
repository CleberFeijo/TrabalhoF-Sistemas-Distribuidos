from pymongo import MongoClient
from pymongo.collection import Collection
from core.config import settings
from loguru import logger
from datetime import datetime


class MongoDatabase:
    def __init__(self, uri: str, db_name: str):
        """
        Inicializa o cliente MongoDB e seleciona o banco de dados.

        :param uri: URI de conexão com o MongoDB.
        :param db_name: Nome do banco de dados.
        """
        self.client = MongoClient(uri)
        self.database = self.client[db_name]

    def get_collection(self, collection_name: str) -> Collection:
        """
        Retorna uma coleção do banco de dados.

        :param collection_name: Nome da coleção.
        :return: Instância da coleção.
        """
        return self.database.get_collection(collection_name)


# Função de inicialização para criar as coleções
def initialize_collections(db: MongoDatabase):
    """
    Inicializa todas as coleções utilizadas na aplicação.

    :param db: Instância de MongoDatabase.
    :return: Dicionário com todas as coleções.
    """
    return {
        "histories_collection": db.get_collection("histories"),
        "users_collection": db.get_collection("users"),
        "api_key_collection": db.get_collection("api_key"),
        "roles_collection": db.get_collection("roles")
    }


# Configuração do cliente MongoDB e inicialização das coleções
logger.info(f"DEBUG_MODE: {settings.MONGO_DEBUG}")

mongo_uri = settings.mongo_uri
db_name = settings.MONGO_DATABASE

mongo_db = MongoDatabase(uri=mongo_uri, db_name=db_name)
collections = initialize_collections(mongo_db)

# Expondo as coleções para uso
histories_collection = collections["histories_collection"]
users_collection = collections["users_collection"]
api_key_collection = collections["api_key_collection"]
roles_collection = collections["roles_collection"]

histories_collection.create_index([("location", "2dsphere")])

def populate_database():
    # Dados para a coleção de usuários
    users = [
        {
            "name": "Cleber",
            "last_name": "Feijo",
            "email": "cleberfeijo@id.uff.br",
            "roles": ["admin", "user", "developer", "customer", "advisor"],
            "hashed_password": "$2b$12$k50KnEhGCP30B5HEblxneeB0y319TOhp9LuaOrINJH/HWs3E5l52G"
        },
        {
            "name": "Luan",
            "last_name": "Freire",
            "email": "luan.freire@id.uff.br",
            "roles": ["admin", "user", "developer", "customer", "advisor"],
            "hashed_password": "$2b$12$k50KnEhGCP30B5HEblxneeB0y319TOhp9LuaOrINJH/HWs3E5l52G"
        },
        {
            "name": "Alessandro",
            "last_name": "Copetti",
            "email": "alessandro.copetti@id.uff.br",
            "roles": ["admin", "user", "developer", "customer", "advisor"],
            "hashed_password": "$2b$12$O6sCiUQ9gb8ICQJYoKJsIuKWkXPaqtofeqIvmk2qALfjGEDqx7yiK"
        }
    ]
    users_collection.insert_many(users)

    # Dados para a coleção de histórias
    histories = [
        {
            "curiosity": "Essa é uma curiosidade.",
            "location": {
                "type": "Point",
                "coordinates": [-41.9237467, -22.5031633]
            },
            "email": "cleberfeijo@id.uff.br",
            "update": "1737516146.109962"
        },
        {
            "curiosity": "Essa é uma outra curiosidade.",
            "location": {
                "type": "Point",
                "coordinates": [-41.9237467, -22.5031633]
            },
            "email": "cleberfeijo@id.uff.br",
            "update": "1737516146.109964"
        },
        {
            "curiosity": "Essa é uma curiosidade inserida por outro usuário.",
            "location": {
                "type": "Point",
                "coordinates": [-41.9237467, -22.5031633]
            },
            "email": "luan.freire@id.uff.br",
            "update": "1737516146.109965"
        }
    ]
    histories_collection.insert_many(histories)

    # Dados para a coleção de papéis (roles)
    roles = [
        {
            "last_update": datetime.now().isoformat(),
            "scope": "company",
            "ownership": "self",
            "permissions": {
                "errors": {"view": True, "create": True, "update": True, "delete": True},
                "headers-options": {"view": True, "create": True, "update": True, "delete": True},
                "users": {"view": True, "create": True, "update": True, "delete": True},
                "roles": {"view": True, "create": True, "update": True, "delete": True},
            },
            "level": 1,
            "role": "user"
        },
        {
            "last_update": datetime.now().isoformat(),
            "scope": "company",
            "ownership": "company",
            "permissions": {
                "errors": {"view": True, "create": True, "update": True, "delete": True},
                "headers-options": {"view": True, "create": True, "update": True, "delete": True},
                "users": {"view": True, "create": True, "update": True, "delete": True},
                "roles": {"view": True, "create": True, "update": True, "delete": True},
            },
            "level": 3,
            "role": "advisor"
        },
        {
            "last_update": datetime.now().isoformat(),
            "scope": "global",
            "ownership": "all",
            "permissions": {
                "errors": {"view": True, "create": True, "update": True, "delete": True},
                "headers-options": {"view": True, "create": True, "update": True, "delete": True},
                "users": {"view": True, "create": True, "update": True, "delete": True},
                "roles": {"view": True, "create": True, "update": True, "delete": True},
            },
            "level": 4,
            "role": "developer"
        },
        {
            "last_update": datetime.now().isoformat(),
            "scope": "global",
            "ownership": "all",
            "permissions": {
                "errors": {"view": True, "create": True, "update": True, "delete": True},
                "headers-options": {"view": True, "create": True, "update": True, "delete": True},
                "users": {"view": True, "create": True, "update": True, "delete": True},
                "roles": {"view": True, "create": True, "update": True, "delete": True},
            },
            "level": 5,
            "role": "customer"
        },
        {
            "last_update": datetime.now().isoformat(),
            "scope": "global",
            "ownership": "all",
            "permissions": {
                "errors": {"view": True, "create": True, "update": True, "delete": True},
                "headers-options": {"view": True, "create": True, "update": True, "delete": True},
                "users": {"view": True, "create": True, "update": True, "delete": True},
                "roles": {"view": True, "create": True, "update": True, "delete": True},
            },
            "level": 6,
            "role": "admin"
        }
    ]
    roles_collection.insert_many(roles)

# Popula o banco de dados

