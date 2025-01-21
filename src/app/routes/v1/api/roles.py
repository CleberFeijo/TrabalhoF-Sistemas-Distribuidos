from fastapi import APIRouter, Depends

from ..deps import get_current_user
from utils.fastapi.models.response import (
    ResponseModelDict,
    ResponseModelList,
)
from crud.crud_roles import CRUDRoles
from pydantic import BaseModel

__all__ = 'router',

router = APIRouter(prefix='/roles', tags=['Roles'])


@router.get("")
def get_all_roles(user=Depends(get_current_user)):
    """
    Endpoint para obter todos os roles.
    Recebe o usuário como parâmetro para ser utilizado dentro da classe CRUDRoles.
    """
    rolesObj = CRUDRoles(user=user)
    roles = rolesObj.get_all_roles()
    return ResponseModelList(message="Success", data=roles)


@router.get("/{role_id}")
def get_role_by_id(role_id: str, user=Depends(get_current_user)):
    """
    Endpoint para buscar um role pelo seu _id.
    Recebe o usuário como parâmetro para ser utilizado dentro da classe CRUDRoles.
    """
    rolesObj = CRUDRoles(user=user)
    role = rolesObj.get_role_by_id(role_id)
    if role:
        return ResponseModelDict(message="Success", data=role)
    return ResponseModelDict(message="Role não encontrado", data={})


@router.get("/role/{role_name}")
def get_role_by_role(role_name: str, user=Depends(get_current_user)):
    """
    Endpoint para buscar um role pelo campo 'role'.
    """
    rolesObj = CRUDRoles(user=user)
    role = rolesObj.get_role_by_role(role_name)
    if role:
        return ResponseModelDict(message="Success", data=role)
    return ResponseModelDict(message="Role não encontrado", data={})


@router.post("")
def create_role(role_data: dict, user=Depends(get_current_user)):
    """
    Endpoint para criar um novo role.
    Recebe o usuário como parâmetro para ser utilizado dentro da classe CRUDRoles.
    """
    rolesObj = CRUDRoles(user=user)
    role_id = rolesObj.create_role(role_data)
    return ResponseModelDict(message="Role criado com sucesso", data={"role_id": role_id})

class RoleUpdateRequest(BaseModel):
    role: str
    scope: str
    ownership: str
    permissions: dict

@router.put("/{role_id}")
def update_role(
    role_id: str,  # O parâmetro de URL
    role_data: RoleUpdateRequest,  # O corpo da requisição, que é mapeado para a classe RoleUpdateRequest
    user=Depends(get_current_user)  # O usuário que está fazendo a requisição
):
    """
    Endpoint para atualizar um role existente.
    Recebe o usuário como parâmetro para ser utilizado dentro da classe CRUDRoles.
    """
    rolesObj = CRUDRoles(user=user)  # Passando o usuário para o construtor da classe CRUDRoles
    
    # Passa os dados para a função de atualização da classe CRUDRoles
    result = rolesObj.update_role(
        role_id=role_id, 
        role=role_data.role, 
        scope=role_data.scope, 
        ownership=role_data.ownership, 
        permissions=role_data.permissions
    )
    
    return ResponseModelDict(message=result["message"], data={})


@router.delete("/{role_id}")
def delete_role(role_id: str, user=Depends(get_current_user)):
    """
    Endpoint para excluir um role.
    Recebe o usuário como parâmetro para ser utilizado dentro da classe CRUDRoles.
    """
    rolesObj = CRUDRoles(user=user)
    result = rolesObj.delete_role(role_id)
    return ResponseModelDict(message=result["message"], data={})
