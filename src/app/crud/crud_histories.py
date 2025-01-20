from typing import List, Optional
from utils.fastapi.models.users import UserModel, UserUpdateModel
from utils.fastapi.schemas.users import UserCreateSchema, UserLogSchema, UserCreateBasicSchema
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from loguru import logger
from core.database.connections import users_collection
import os
from core.security import verify_password, get_password_hash
from core.permission import UserPermission


class CRUDHist():
    ## Done
    def create_user(self, user: UserCreateBasicSchema):
        self.can_create()

        default_password = os.getenv("USER_DEFAULT_PASSWORD")

        hashed_password = get_password_hash(default_password)

        new_user = UserModel(
            name=user.name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=hashed_password,
        ).__dict__

        try:
            result = users_collection.insert_one(new_user)
            logger.info("User created successfully!")
            created_user = users_collection.find_one(
                {"_id": result.inserted_id},
                {"hashed_password": 0, "pedmais_info.token": 0},
            )
            return created_user
        except DuplicateKeyError as e:
            field = list(e.details.get("keyPattern", {}).keys())[0]
            value = list(e.details.get("keyValue", {}).values())[0]
            logger.error(
                f"Duplicated Key Error on field '{field}' with value '{value}'"
            )
            raise Exception(
                f"{field.capitalize()} '{value}' is already in use."
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise e

    def get_user_by_id(self, user_id: ObjectId):
        self.can_view()

        user = users_collection.find_one(
            {"_id": user_id}, {"hashed_password": 0}
        )
        return user  # Retorne o usuário ou None

    def get_multi_users(self, filters=None):
        self.can_view()

        query = {
            **self.query_obj,
        }

        # Se filtros forem fornecidos, aplica-os
        if filters:
            query.update(filters)

        return list(
            users_collection.find(
                query, {"hashed_password": 0}
            ).sort("_id", -1)
        )

    def update_user(self, user_id: ObjectId, user: UserUpdateModel):
        self.can_update()

        update_fields = {}
        if user.name:
            update_fields["name"] = user.name
        if user.last_name:
            update_fields["last_name"] = user.last_name
        if user.email:
            update_fields["email"] = user.email

        if not update_fields:
            raise ValueError("No valid fields to update.")

        result = users_collection.update_one(
            {"_id": user_id},
            {"$set": update_fields},
        )

        # Se modified_count for 0, significa que não houve alteração ou o usuário não foi encontrado
        if result.matched_count == 0:
            raise ValueError("User not found.")

        if result.modified_count == 0:
            logger.info("No changes made. Values are identical.")
            return {"message": "No changes made. Values are identical."}

        logger.info("User updated successfully!")
        return users_collection.find_one(
            {"_id": user_id}, {"hashed_password": 0, "pedmais_info.token": 0}
        )

    def update_user_password(self, password: str):
        # Caso contrário, fazemos a atualização
        hashed_password = get_password_hash(password)
        result = users_collection.update_one(
            {"_id": self.user.id}, {"$set": {"hashed_password": hashed_password}}
        )

        if result.modified_count == 0:
            raise ValueError("User not found.")

        logger.info("User password updated successfully!")
        return users_collection.find_one(
            {"_id": self.user.id}, {"hashed_password": 0}
        )

    def verify_password(self, password: str):
        user = users_collection.find_one({"_id": self.user.id})
        if not verify_password(password, user.get("hashed_password")):
            return None
        return True

    def delete_user(self, user_id: ObjectId):
        self.can_delete()

        result = users_collection.delete_one({"_id": user_id})
        if result.deleted_count == 0:
            raise ValueError("User not found.")
        logger.info("User deleted successfully!")
        return True

    @staticmethod
    def get_multi() -> List[dict]:
        return list(
            users_collection.find({}, {"hashed_password": 0})
        )

    @staticmethod
    def get_by_id(id_: ObjectId) -> Optional[dict]:
        return users_collection.find_one({"_id": id_})

    @staticmethod
    def get_by_email(email: str):
        return users_collection.find_one({"email": email})

    @staticmethod
    def create(user: UserCreateSchema):
        hashed_password = get_password_hash(user.password)

        new_user = UserModel(
            name=user.name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=hashed_password,
        ).__dict__
        try:
            result = users_collection.insert_one(new_user)
            logger.info("User created successfully!")
            return result
        except DuplicateKeyError:
            logger.error("Duplicated Key Error!")
            raise Exception('User information is not unique')

    @staticmethod
    def logged(user_logged: UserLogSchema) -> None:
        _ = users_collection.update_one(
            {"_id": user_logged.user_id}, {"$set": {"logged": user_logged.logged}}
        )

    @staticmethod
    def verify_log(id_: ObjectId) -> bool:
        result = users_collection.find_one({"_id": id_})
        return bool(result.get("logged"))
