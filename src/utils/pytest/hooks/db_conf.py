try:
    import pytest

    from typing import Iterable, Type

    from utils.pymongo import ConnectionTypeEnum, MongoCollection, MongoModel

    from ._base import *

    __all__ = 'PytestMongoDBConf',


    class PytestMongoDBConf(PytestHook):
        def __init__(self, collection: Type[MongoCollection], models: Iterable[MongoModel] = None):
            self.collection = collection(connection=ConnectionTypeEnum.TEST)
            self.models = models

        def on_configure(self, config: pytest.Config):
            self.collection.delete_many({})  # Sempre começa limpando a coleção.
            if self.models:
                self.collection.insert_many(self.models, keep_id=True)
            if self.collection.Indexes:
                self.collection.create_indexes()

        def on_sessionstart(self, session: pytest.Session):
            pass

        def on_sessionfinish(self, session: pytest.Session):
            pass

        def on_unconfigure(self, config: pytest.Config):
            self.collection.drop_collection()

# Usado somente quando 'utils.pymongo' for importado junto com o projeto.
except ImportError:
    pass
