# import pymongo
from utils.pydantic import BaseModel, ObjectIdField
from datetime import datetime
from typing import List, Optional


class UserShortView(BaseModel):
    name: str
    last_name: str
    role: str


class UserUpdatePasswordModel(BaseModel):
    current_password: str
    new_password: str


class UserCreationModel(BaseModel):
    name: str
    last_name: str
    email: str


class ListUserPerPageModel(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class UserUpdateModel(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    pedmais_info: Optional[dict] = None
    roles: Optional[List[str]] = []


class UserModel(BaseModel):
    name: str
    last_name: str
    roles: List[str]
    email: str
    hashed_password: str
    pedmais_info: Optional[dict] = None


class LogTimeModel(BaseModel):
    user_id: ObjectIdField
    last_logged: datetime


class LogVerifyModel(BaseModel):
    logging_time: datetime
