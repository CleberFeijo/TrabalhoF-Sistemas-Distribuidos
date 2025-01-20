from utils.fastapi.schemas.users import UserRouteSchema
from core.database.connections import roles_collection


class UserPermission:
    permission = {
        "ownership": "self",
        "scope": "company",
        "view": False,
        "create": False,
        "update": False,
        "delete": False,
    }

    def __init__(self, user: UserRouteSchema, permission_name: str):
        self.user = user
        self.permission_name = permission_name
        self.company_id = self.getCompanyId()
        self.permissions = self.get_roles_by_names__(self.user.roles)
        self.permission = self.get_highest_permission()
        self.query_obj = self.create_query_obj()

    def get_roles_by_names__(self, role_names: list):
        try:
            roles = list(
                roles_collection.find(
                    {"role": {"$in": role_names}}, {"_id": 0, "last_update": 0}
                ).sort("level", -1)
            )
            return roles
        except Exception as e:
            print(e)
            print(f"Erro ao buscar roles por nomes: {e}")
            return

    def getUserId(self):
        try:
            return self.user.id
        except AttributeError:
            try:
                return self.user["id"]
            except (TypeError, KeyError):
                try:
                    return self.user["_id"]
                except (TypeError, KeyError):
                    raise ValueError("User ID not found")

    def getCompanyId(self):
        try:
            return self.user.company_id
        except AttributeError:
            try:
                return self.user["company_id"]
            except (TypeError, KeyError):
                raise ValueError("Company ID not found")

    def create_query_obj(self):
        query_obj = {}
        if self.permission["scope"] == "company":
            query_obj["company_id"] = self.company_id

        if self.permission["ownership"] == "self":
            query_obj["user_id"] = self.getUserId()

        return query_obj

    def get_highest_permission(self):
        permissions = self.permissions

        highest_permission_level = -1
        permission_details = {
            "ownership": "self",
            "scope": "company",
            "view": False,
            "create": False,
            "update": False,
            "delete": False,
        }

        permission_name = self.permission_name

        for permission in permissions:
            if (
                permission["permissions"].get(permission_name)
                and permission["level"] > highest_permission_level
            ):
                highest_permission_level = permission["level"]

                permission_details["view"] = permission["permissions"][
                    permission_name
                ].get("view", False)
                permission_details["create"] = permission["permissions"][
                    permission_name
                ].get("create", False)
                permission_details["update"] = permission["permissions"][
                    permission_name
                ].get("update", False)
                permission_details["delete"] = permission["permissions"][
                    permission_name
                ].get("delete", False)

                permission_details["ownership"] = permission.get("ownership", "self")
                permission_details["scope"] = permission.get("scope", "company")

        self.query_obj = {}

        if permission_details["scope"] == "company":
            self.query_obj["company_id"] = self.company_id

        if permission_details["ownership"] == "self":
            self.query_obj["user_id"] = self.getUserId()

        return permission_details

    def can_view(self):
        if self.permission["view"]:
            return True
        raise Exception('O Usuário não tem permissão para executar essa ação.')

    def can_create(self):
        if self.permission["create"]:
            return True
        raise Exception('O Usuário não tem permissão para executar essa ação.')

    def can_update(self):
        if self.permission["update"]:
            return True
        raise Exception('O Usuário não tem permissão para executar essa ação.')

    def can_delete(self):
        if self.permission["delete"]:
            return True
        raise Exception('O Usuário não tem permissão para executar essa ação.')
