from core.database.connections import api_key_collection
import secrets
from datetime import datetime
from pymongo import ReturnDocument
from pytz import utc
from core.permission import UserPermission


class CRUDAPIKeys(UserPermission):
    def __init__(self, user) -> None:
        self.user = user
        super().__init__(user, "api-keys")

    def get_api_keys(self):
        self.can_view()

        results = api_key_collection.find({**self.query_obj, "user_id": self.user.id})
        api_keys = list(results)
        return api_keys

    def createNewApiKey(self, service="pedmais"):
        self.can_create()

        newApiKey = secrets.token_urlsafe(42)

        try:
            result = api_key_collection.insert_one(
                {
                    "user_id": self.user.id,
                    "api_key": newApiKey,
                    "service": service,
                    "created_at": datetime.now(tz=utc),
                    "last_used": None,
                    "expiration": None,
                    "times_used": 0,
                }
            )

            # Recuperar o documento completo usando o ID recém-inserido
            inserted_document = api_key_collection.find_one({"_id": result.inserted_id})

            return inserted_document
        except Exception as e:
            print(e)
            return None

    def validateApiKey(self, apiKey):
        self.can_view()

        try:
            result = api_key_collection.find_one(
                {**self.query_obj, "user_id": self.user.id}
            )

            print(result)

            if result.api_key != apiKey:
                return False

            return True
        except Exception as e:
            print(e)
            return False

    def refreshApiKey(self):
        self.can_update()

        try:
            refresed = secrets.token_urlsafe(42)
            result = api_key_collection.update_one(
                {**self.query_obj, "user_id": self.user.id},
                {"$set": {"api_key": refresed}},
            )

            # Se houve uma modificação, buscar o documento atualizado
            if result.modified_count:
                updated_document = api_key_collection.find_one(
                    {"user_id": self.user.id}
                )
                return updated_document
            return None
        except Exception as e:
            print(e)
            return None

    def deleteApiKey(self):
        self.can_delete()

        try:
            print("entrou aqui ")
            result = api_key_collection.delete_one(
                {**self.query_obj, "user_id": self.user.id}
            )
            print(result)
            if result.deleted_count:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def getUserIdByApiKey(apiKey):
        try:
            result = api_key_collection.find_one({"api_key": apiKey})
            if not result:
                return None

            return result["user_id"]
        except:
            return None

    @staticmethod
    def updateUsageStats(apiKey):
        try:
            result = api_key_collection.find_one_and_update(
                {"api_key": apiKey},
                {
                    "$inc": {"times_used": 1},
                    "$set": {"last_used": datetime.now(tz=utc)},
                },
                return_document=ReturnDocument.AFTER,
            )
            return result
        except Exception as e:
            print(e)
            return None
