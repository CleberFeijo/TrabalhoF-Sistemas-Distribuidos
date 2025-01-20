from core.database.connections import roles_collection
from datetime import datetime
from bson import ObjectId
from pytz import utc
from core.permission import UserPermission
from utils.fastapi.schemas.users import UserRouteSchema


class CRUDRoles(UserPermission):
    def __init__(self, user: UserRouteSchema):
        """
        Construtor da classe CRUDRoles. Recebe o usuário como parâmetro.
        :param user: O usuário que está fazendo a requisição.
        """
        super().__init__(user, "roles")  # Chama o construtor da classe UserPermission

    def get_all_roles(self):
        """
        Retorna todos os papéis da coleção roles.
        """
        self.can_view()

        return list(roles_collection.find())  # Retorna todos os documentos da coleção

    def get_role_by_id(self, role_id: str):
        """
        Retorna um role específico pelo _id.
        """
        self.can_view()
        try:
            return roles_collection.find_one({"_id": ObjectId(role_id)})
        except Exception as e:
            print(f"Erro ao buscar role por id: {e}")
            return None

    def get_role_by_role(self, role_name: str):
        """
        Retorna um role específico pelo campo 'role'.
        """
        self.can_view()
        return roles_collection.find_one({"role": role_name})

    def get_roles_by_names(self, role_names: list):
        """
        Retorna uma lista de roles com base em uma lista de nomes de roles.
        """
        self.can_view()
        try:
            roles = list(
                roles_collection.find(
                    {"role": {"$in": role_names}}, {"_id": 0, "last_update": 0}
                ).sort("level", -1)
            )
            return roles
        except Exception as e:
            print(f"Erro ao buscar roles por nomes: {e}")
            return []

    def create_role(self, role_data: dict):
        """
        Cria um novo role na coleção.
        """
        self.can_create()
        now = datetime.now(tz=utc)
        role_data["last_update"] = now
        result = roles_collection.insert_one(role_data)
        return str(result.inserted_id)

    def update_role(
        self, role_id: str, role: str, scope: str, ownership: str, permissions: dict
    ):
        """
        Atualiza o role com base no _id.
        """
        self.can_update()
        now = datetime.now(tz=utc)
        update_data = {
            "role": role,
            "scope": scope,
            "ownership": ownership,
            "permissions": permissions,
            "last_update": now,
        }

        try:
            result = roles_collection.update_one(
                {"_id": ObjectId(role_id)},  # Filtro pelo _id
                {"$set": update_data},  # Atualiza os dados
            )

            if result.modified_count == 0:
                return {"message": "Role não encontrado ou sem alterações."}

            return {"message": "Role atualizado com sucesso."}
        except Exception as e:
            print(f"Erro ao atualizar role: {e}")
            return {"message": "Erro ao atualizar role."}

    def update_permissions(self, role_id: str, permissions: dict):
        """
        Atualiza as permissões do role com base no _id.
        """
        self.can_update()
        try:
            result = roles_collection.update_one(
                {"_id": ObjectId(role_id)},  # Filtro pelo _id
                {
                    "$set": {
                        "permissions": permissions,
                        "last_update": datetime.now(tz=utc),
                    }
                },  # Atualiza permissões e last_update
            )

            if result.modified_count == 0:
                return {"message": "Role não encontrado ou sem alterações."}

            return {"message": "Permissões atualizadas com sucesso."}
        except Exception as e:
            print(f"Erro ao atualizar permissões: {e}")
            return {"message": "Erro ao atualizar permissões."}

    def delete_role(self, role_id: str):
        """
        Exclui um role baseado no _id.
        """
        self.can_delete()
        try:
            result = roles_collection.delete_one({"_id": ObjectId(role_id)})
            if result.deleted_count == 0:
                return {"message": "Role não encontrado."}
            return {"message": "Role excluído com sucesso."}
        except Exception as e:
            print(f"Erro ao excluir role: {e}")
            return {"message": "Erro ao excluir role."}
