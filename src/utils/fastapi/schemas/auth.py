from pydantic import EmailStr
from utils.pydantic import BaseModel


class LoginAttempt(BaseModel):
    email: EmailStr
    password: str


class CreateUserAsAdmin(BaseModel):
    name: str
    last_name: str
    role: str
    email: EmailStr
    password: str
    admin_password: str


class ValidatePedmaisUser(BaseModel): 
    email: str
    token: str 

class ResponseToken(BaseModel):
    """Modelo de token de resposta."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int

