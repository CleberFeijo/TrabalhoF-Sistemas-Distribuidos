from fastapi import WebSocket
from bson import ObjectId


class ConnectionManager:
    def __init__(self):
        self.active_connections: list = []

    async def connect(self, id_: ObjectId, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append({id_: websocket})

    def disconnect(self, id_: ObjectId, websocket: WebSocket, last_message: str):
        if last_message != "----Fim----":
            self.active_connections.remove({id_: websocket})
            return
        aux_connections = self.active_connections
        for connection in aux_connections:
            if id_ in connection.keys():
                self.active_connections.remove(connection)

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, id_: ObjectId, message: str):
        for connection in self.active_connections:
            if id_ in connection.keys():
                await connection[id_].send_text(data=message)
