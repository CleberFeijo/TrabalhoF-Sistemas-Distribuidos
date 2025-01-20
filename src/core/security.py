from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Form
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


class OAuth2ClientCredentialsRequestForm:
    """
    Implementação de formulário para o fluxo de *client credentials* (OAuth2).

    Baseado na classe :class:`fastapi.security.oauth2.OAuth2PasswordRequestForm`.
    """

    def __init__(
        self,
        grant_type: str = Form(default=None, regex="client_credentials"),
        scope: str = Form(default=""),
        client_id: Optional[str] = Form(default=None),
        client_secret: Optional[str] = Form(default=None),
    ):
        self.grant_type = grant_type
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


class OAuth2CustomBearer(OAuth2):
    """Implementação de bearer para suportar os fluxos de *password* e
    *client credentials* (OAuth2).

    Baseado na classe :class:`fastapi.security.oauth2.OAuth2PasswordBearer`.
    """

    def __init__(
        self,
        password_token_url: str,
        client_credentials_token_url: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            clientCredentials={  # type: ignore
                "tokenUrl": client_credentials_token_url,
                "scopes": scopes,
            },
            password={"tokenUrl": password_token_url, "scopes": scopes},  # type: ignore
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)
