from pymongo import MongoClient
from pymongo.collection import Collection
from core.config import settings
from loguru import logger


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
