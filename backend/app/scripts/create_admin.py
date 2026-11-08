"""Cria um administrador ou promove um usuário existente.

Uso (dentro do container):
    python -m app.scripts.create_admin email@exemplo.com --name "Nome" --last-name "Sobrenome"

A senha é pedida no terminal (não fica no histórico do shell).
"""
import argparse
import asyncio
import getpass

from app.db import mongo
from app.models.user import Role
from app.repositories import users as users_repo


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email")
    parser.add_argument("--name", default="Administrador")
    parser.add_argument("--last-name", default="")
    args = parser.parse_args()

    db = await mongo.connect()
    try:
        existing = await users_repo.get_by_email(db, args.email)
        if existing:
            roles = sorted(set(existing.get("roles", [])) | {Role.USER.value, Role.ADMIN.value})
            await users_repo.bump_token_version(db, existing["_id"], {"roles": roles})
            print(f"Usuário {args.email} promovido a admin.")
            return
        password = getpass.getpass("Senha (mín. 8 caracteres): ")
        if len(password) < 8 or password != getpass.getpass("Confirme a senha: "):
            raise SystemExit("Senha inválida ou não confere.")
        await users_repo.create(db, name=args.name, last_name=args.last_name, email=args.email,
                                password=password, roles=[Role.USER, Role.ADMIN])
        print(f"Administrador {args.email} criado.")
    finally:
        await mongo.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
