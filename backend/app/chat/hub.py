"""Gerencia as conexões WebSocket locais deste processo, agrupadas por sala."""
import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field

from fastapi import WebSocket

logger = logging.getLogger("hist.chat.hub")


@dataclass(eq=False)
class Connection:
    websocket: WebSocket
    room: str
    user_id: str
    user_name: str
    latitude: float
    longitude: float
    _sent: deque = field(default_factory=deque)

    def allow_message(self, max_messages: int, window_s: float) -> bool:
        """Limite simples por janela deslizante (anti-flood)."""
        now = time.monotonic()
        while self._sent and now - self._sent[0] > window_s:
            self._sent.popleft()
        if len(self._sent) >= max_messages:
            return False
        self._sent.append(now)
        return True


class ChatHub:
    def __init__(self, broker) -> None:
        self.broker = broker
        self._rooms: dict[str, set[Connection]] = defaultdict(set)

    async def start(self) -> None:
        await self.broker.start(self._deliver)

    async def stop(self) -> None:
        await self.broker.stop()
        for conns in list(self._rooms.values()):
            for conn in list(conns):
                try:
                    await conn.websocket.close(code=1001, reason="Servidor reiniciando.")
                except Exception:
                    pass
        self._rooms.clear()

    def join(self, conn: Connection) -> None:
        self._rooms[conn.room].add(conn)

    def leave(self, conn: Connection) -> None:
        conns = self._rooms.get(conn.room)
        if conns is None:
            return
        conns.discard(conn)
        if not conns:
            self._rooms.pop(conn.room, None)

    def local_count(self, room: str) -> int:
        return len(self._rooms.get(room, ()))

    async def publish(self, room: str, event: dict) -> None:
        await self.broker.publish(room, event)

    async def _deliver(self, room: str, event: dict) -> None:
        conns = list(self._rooms.get(room, ()))
        if not conns:
            return
        results = await asyncio.gather(
            *(c.websocket.send_json(event) for c in conns), return_exceptions=True
        )
        # Conexões que falharam (cliente caiu sem fechar) saem da sala.
        for conn, result in zip(conns, results, strict=True):
            if isinstance(result, Exception):
                logger.debug("Removendo conexão morta da sala %s: %s", room, result)
                self.leave(conn)
