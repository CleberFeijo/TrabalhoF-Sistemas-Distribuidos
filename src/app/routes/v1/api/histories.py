from fastapi_restful.cbv import cbv
from fastapi import APIRouter, Depends, HTTPException, Query
from app.crud.crud_user import CRUDUser
from ..deps import get_current_user
from utils.fastapi.models.response import ResponseModel
from utils.fastapi.models.response import ResponseModelDict, ResponseModelList
from utils.fastapi.models.users import (
    UserCreationModel,
    # UserUpdateRolesModel,
    UserUpdateModel,
    UserUpdatePasswordModel,
    ListUserPerPageModel,
)
from utils.pydantic import ObjectIdField
from loguru import logger

from utils.fastapi import OpenAPISchemaFactory

__all__ = 'router',

router = APIRouter(prefix='/exemplo', tags=['Exemplo'])


@cbv(router)
class User:

    @router.get(
        path='/',
        responses=OpenAPISchemaFactory(200),
        summary="User information",
        description="Returns the user's relevant information and some configuration parameters for frontend customization.",
    )
    def getLoggedUserProfile(self, user=Depends(get_current_user)):
        try:
            response = CRUDUser(user).get_user_by_id(user.id)
            user_dict = {
                "_id": str(response["_id"]),
                "name": response["name"],
                "lastname": response["last_name"],
                "email": response["email"],
            }

            return ResponseModelDict(
                message="User information returned successfully!", data=user_dict
            )
        except Exception as e:
            logger.error(f"Unexpected error in retrieving user profile: {e}")
            raise e

    @router.post(
        path='/',
        responses=OpenAPISchemaFactory(200),
    )
    def cadastro(self, body: UserCreationModel, user=Depends(get_current_user)):
        try:
        # Try to create the user
            new_user = CRUDUser(user).create_user(body)
            return ResponseModelDict(message="User created successfully!", data=new_user)
        except Exception as e:
            # Capture unexpected errors and return an HTTP 500 error
            logger.error(f"Unexpected error during user creation: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
        
    @router.get("/{user_id}")
    def getUsersById(user_id: ObjectIdField, user=Depends(get_current_user)):
        try:
            user_data = CRUDUser(user).get_user_by_id(user_id)
            if not user_data:
                raise HTTPException(status_code=404, detail="User not found")
            return ResponseModelDict(
                message=f"User with id {user_id} returned successfully!", data=user_data
            )
        except HTTPException as e:
            logger.error(f"HTTP Error in getting user by id {user_id}: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in getting user by id {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @router.patch(
        path='/password',
        responses=OpenAPISchemaFactory(200),
    )
    def atualizacao(
        self, 
        passwords: UserUpdatePasswordModel,
        user=Depends(get_current_user)
    ):
        try:
            # Check if the current password is valid
            obj = CRUDUser(user)

            if not obj.verify_password(passwords.current_password):
                raise HTTPException(status_code=400, detail="Current password is invalid")

            updated_user = obj.update_user_password(passwords.new_password)

            return ResponseModelDict(
                message="User password updated successfully!", data=updated_user
            )
        except HTTPException as e:
            logger.error(f"HTTP Error during password update: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during password update: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    
    @router.put("/{user_id}")
    def update_user(
        self,
        user_id: ObjectIdField, 
        body: UserUpdateModel, 
        user=Depends(get_current_user)
    ):
        try:
            updated_user = CRUDUser(user).update_user(user_id, body)

            # If the return contains a message, it means no changes were made, so we return that
            if isinstance(updated_user, dict) and "message" in updated_user:
                return ResponseModelDict(message=updated_user["message"], data=None)
            return ResponseModelDict(
                message="User updated successfully!", data=updated_user
            )
        except Exception as e:
            logger.error(f"Unexpected error in updating user with id {user_id}: {str(e)}")
            raise HTTPException(status_code=403, detail=str(e))


    @router.delete("/{user_id}")
    def deleteUser(
        self,
        user_id: ObjectIdField, 
        user=Depends(get_current_user)
    ):
        try:
            # Delete the user
            CRUDUser(user).delete_user(user_id)

            return ResponseModelDict(
                message="User deleted successfully!", data={"user_id": user_id}
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                logger.error(f"HTTP Error during user deletion: {e.detail}")
                raise e
            logger.error(f"Unexpected error during user deletion: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
