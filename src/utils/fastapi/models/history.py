from pydantic import EmailStr
from utils.pydantic import ObjectIdField, BaseModel


class HistoryCreationModel(BaseModel):
    curiosity: str
    location: str
    email: str

class HistoryGetModel(BaseModel):
    location: str
    email: str