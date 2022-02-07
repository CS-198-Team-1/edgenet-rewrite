import uuid, asyncio, json
import websockets
from message import EdgeNetMessage


class EdgeNetClient:
    def __init__(self, server_url, session_id=None):
        self.server_url = server_url

        # Generate a random UUID if not given
        if session_id is None:
            self.session_id = str(uuid.uuid4())
        else:
            self.session_id = session_id

        # Connection is initially null
        self.connection = None

    def run(self):
        asyncio.run(self.perform_handshake())

    async def perform_handshake(self):
        while True:
            try:
                self.connection = await websockets.connect(self.server_url)
                break
            except ConnectionRefusedError:
                # TODO: Implement exponential backoff for reconnecting
                pass
            
        handshake_message = EdgeNetMessage.create_client_handshake_message(self.session_id)
        await self.send(handshake_message)
        await self.connection.close()

    async def send(self, message: EdgeNetMessage):
        await self.connection.send(json.dumps({
            "session_id": message.session_id,
            "msg_type": message.msg_type
        }))