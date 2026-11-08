"""Distribuição de eventos do chat entre processos.

Cada processo da API mantém apenas as conexões WebSocket que ele mesmo
aceitou. Para que uma mensagem chegue a usuários conectados em outros
processos (vários workers do uvicorn ou várias instâncias), os eventos são
publicados no Redis (pub/sub) e cada processo repassa às suas conexões locais.

Sem REDIS_URL, usa-se um broker em memória — suficiente para 1 processo.
"""
import asyncio
import contextlib
import json
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger("hist.chat.broker")

Handler = Callable[[str, dict], Awaitable[None]]
CHANNEL_PREFIX = "hist:chat:"


class InMemoryBroker:
    def __init__(self) -> None:
        self._handler: Handler | None = None

    async def start(self, handler: Handler) -> None:
        self._handler = handler

    async def stop(self) -> None:
        self._handler = None

    async def publish(self, room: str, event: dict) -> None:
        if self._handler is not None:
            await self._handler(room, event)

    async def ping(self) -> bool:
        return True


class RedisBroker:
    """Pub/sub no Redis com uma única assinatura por padrão (`hist:chat:*`).

    Cada processo recebe os eventos de todas as salas e descarta os das salas
    sem conexões locais. Para o volume esperado isso é mais simples e robusto
    do que (des)assinar canais dinamicamente.
    """

    def __init__(self, url: str) -> None:
        from redis import asyncio as aioredis

        self._redis = aioredis.from_url(url, decode_responses=True)
        self._pubsub = None
        self._task: asyncio.Task | None = None

    async def start(self, handler: Handler) -> None:
        await self._redis.ping()
        self._pubsub = self._redis.pubsub(ignore_subscribe_messages=True)
        await self._pubsub.psubscribe(f"{CHANNEL_PREFIX}*")
        self._task = asyncio.create_task(self._listen(handler), name="chat-redis-listener")

    async def _listen(self, handler: Handler) -> None:
        while True:
            try:
                message = await self._pubsub.get_message(timeout=1.0)
                if message is None or message.get("type") != "pmessage":
                    continue
                room = message["channel"][len(CHANNEL_PREFIX):]
                await handler(room, json.loads(message["data"]))
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Falha ao processar evento do Redis; tentando novamente.")
                await asyncio.sleep(1)

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        if self._pubsub is not None:
            await self._pubsub.aclose()
        await self._redis.aclose()

    async def publish(self, room: str, event: dict) -> None:
        await self._redis.publish(f"{CHANNEL_PREFIX}{room}", json.dumps(event, default=str))

    async def ping(self) -> bool:
        try:
            return bool(await self._redis.ping())
        except Exception:
            return False


def build_broker(redis_url: str):
    return RedisBroker(redis_url) if redis_url else InMemoryBroker()
