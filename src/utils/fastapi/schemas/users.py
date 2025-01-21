from pydantic import EmailStr
from datetime import datetime
from utils.pydantic import ObjectIdField, BaseModel
from typing import List, Optional


class UserRouteSchema(BaseModel):
    id: ObjectIdField
    name: str
    last_name: str
    roles: List[str]


class UserSchema(BaseModel):
    _id: ObjectIdField
    name: str
    last_name: str
    email: EmailStr
    hash_password: str
    roles: List[str]


class UserCreateSchema(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    password: str
    roles: List[str]
    pedmais_info: Optional[dict] = None


class UserCreateBasicSchema(BaseModel):
    name: str
    last_name: str
    email: str


class UserLogSchema(BaseModel):
    user_id: ObjectIdField
    logged: bool
