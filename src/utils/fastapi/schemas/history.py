from pydantic import EmailStr
from utils.pydantic import ObjectIdField, BaseModel


class HistoryPostSchema(BaseModel):
    curiosity: str
    location: dict
    email: EmailStr


class HistoryGetSchema(BaseModel):
    location: dict

class MSGPostSchema(BaseModel):
    email: EmailStr
    msg: str
    web_socket: ObjectIdField