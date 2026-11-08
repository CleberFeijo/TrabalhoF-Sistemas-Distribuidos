"""Hash de senhas e emissão/validação de tokens JWT."""
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings

# O bcrypt só considera os primeiros 72 bytes da senha; a validação de
# entrada (models/user.py) rejeita senhas maiores que isso.
BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


# Hash fixo usado para gastar o mesmo tempo quando o email não existe,
# evitando que o tempo de resposta revele quais emails estão cadastrados.
_DUMMY_HASH = bcrypt.hashpw(b"hist-dummy-password", bcrypt.gensalt()).decode("utf-8")


def burn_password_check(password: str) -> None:
    verify_password(password, _DUMMY_HASH)


def create_access_token(user_id: str, token_version: int) -> tuple[str, int]:
    """Retorna (token, expires_in_segundos)."""
    settings = get_settings()
    now = datetime.now(UTC)
    lifetime = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "ver": token_version,
        "type": "access",
        "iat": now,
        "exp": now + lifetime,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, int(lifetime.total_seconds())


def decode_access_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["sub", "exp", "iat", "ver"]},
        )
    except jwt.PyJWTError:
        return None
    if payload.get("type") != "access":
        return None
    return payload
