from typing import Optional
from core.config import settings
from fastapi import Depends, Header, Request
from pydantic import BaseModel
from jose import JWTError, jwt
from app.crud.crud_user import CRUDUser
from datetime import datetime, timedelta
from utils.fastapi.schemas.users import UserRouteSchema
import os
from utils.pydantic import ObjectIdField
from bson import ObjectId
from app.crud.crud_api_key import CRUDAPIKeys
from core.security import OAuth2CustomBearer
import base64
from core.auth import oauth2_scheme


class TokenData(BaseModel):
    id_user: Optional[ObjectIdField] = None


def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> UserRouteSchema:
    try:
        payload: dict = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )

        id_user: Optional[ObjectIdField] = payload.get("sub")
        if id_user is None:
            raise Exception('Could not validate credentials')
        token_data = TokenData(id_user=id_user)
    except JWTError:
        raise Exception('Could not validate credentials')

    crud_user_obj = CRUDUser()
    user = crud_user_obj.get_by_id(token_data.id_user)

    if user is None:
        raise Exception('Could not validate credentials')

    if not user.get("logged"):
        raise Exception("The user has logged out and hasn't logged in since")

    # Other Logic here

    user_route = UserRouteSchema(
        id=str(user["_id"]),
        name=user["name"],
        last_name=user["last_name"],
        company_id=user["company_id"],
        roles=user["roles"],
    )
    return user_route


## Alterando
def get_current_user_by_api_key(Authorization: Optional[str] = Header(None)):
    ## o formato da chave de api que virá em base64 é o seguinte:
    ## email-user@example.com/token:api-key (igual a forma que o zendesk faz)

    if not Authorization:
        print("Authorization header is missing")
        raise Exception('Could not validate credentials')

    if Authorization.startswith("Basic "):
        Authorization = Authorization[len("Basic ") :]
    else:
        print("Authorization header does not start with 'Basic '")
        raise Exception('Could not validate credentials')

    try:
        decoded_key = base64.b64decode(Authorization).decode("utf-8")
    except Exception:
        print("Failed to decode Authorization header")
        raise Exception('Could not validate credentials')

    try:
        email, api_key = decoded_key.split("/token:")
    except ValueError:
        print("Authorization header format is incorrect")
        raise Exception('Could not validate credentials')

    user_id = CRUDAPIKeys.getUserIdByApiKey(api_key)
    crud_user_obj = CRUDUser()
    user = crud_user_obj.get_by_id(user_id)

    if not user:
        print("User not found")
        raise Exception('Could not validate credentials')

    if user["email"] != email:
        print("Email does not match")
        raise Exception('Could not validate credentials')

    CRUDAPIKeys.updateUsageStats(api_key)

    user_route = UserRouteSchema(
        id=str(user["_id"]),
        name=user["name"],
        last_name=user["last_name"],
        company_id=user["company_id"],
        roles=user["roles"],
    )

    return user_route


def generate_ws_token(document_id: ObjectId, user: UserRouteSchema):
    dict_ = {
        "document_id": str(document_id),
        "user": str(user.id),
        "iat": datetime.now().timestamp(),
        "exp": (datetime.now() + timedelta(minutes=30)).timestamp(),
    }
    return jwt.encode(dict_, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_ws_token(token: str):
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
    if payload["exp"] < datetime.now().timestamp():
        return
    user = CRUDUser().get_by_id(ObjectId(payload["user"]))

    if not user.get("logged"):
        raise Exception("The user has logged out and hasn't logged in since")

    user_ = UserRouteSchema(
        id=str(user["_id"]),
        name=user["name"],
        last_name=user["last_name"],
        company_id=user["company_id"],
        role=user["role"],
    )
    return ObjectId(payload["document_id"]), user_
