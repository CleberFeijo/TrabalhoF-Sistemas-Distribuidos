"""Tarefas idempotentes executadas na inicialização."""
import logging

from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import get_settings
from app.core.errors import Conflict
from app.models.user import Role
from app.repositories import users as users_repo

logger = logging.getLogger("hist.bootstrap")


async def ensure_admin(db: AsyncDatabase) -> None:
    """Cria o administrador inicial a partir de ADMIN_EMAIL/ADMIN_PASSWORD.

    Não faz nada se as variáveis estiverem vazias ou se o email já existir
    (nunca sobrescreve senha nem papéis de uma conta existente).
    """
    settings = get_settings()
    if not settings.ADMIN_EMAIL:
        return
    if await users_repo.get_by_email(db, settings.ADMIN_EMAIL):
        return
    try:
        await users_repo.create(
            db,
            name=settings.ADMIN_NAME,
            last_name="",
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            roles=[Role.USER, Role.ADMIN],
        )
        logger.info("Administrador inicial criado: %s", settings.ADMIN_EMAIL)
    except Conflict:
        pass  # outro worker criou ao mesmo tempo
