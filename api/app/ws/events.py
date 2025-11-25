from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[id] = websocket

    def disconnect(self, id: str):
        self.active_connections.pop(id, None)

    async def send_personal_message(self, id: str, message: dict):
        ws = self.active_connections.get(id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, message: dict):
        for ws in list(self.active_connections.values()):
            await ws.send_json(message)

manager = ConnectionManager()