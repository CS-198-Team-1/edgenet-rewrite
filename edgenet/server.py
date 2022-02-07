import asyncio
import websockets
from .session import EdgeNetSession
from .message import EdgeNetMessage
from .constants import *


class EdgeNetServer:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port     = port

        # Set empty dict to store sessions
        self.sessions = {}

    def run(self):
        asyncio.run(self.serve())

    async def serve(self, stop=asyncio.Future()):
        # Main server loop
        async with websockets.serve(self.handler, self.hostname, self.port, ping_timeout=SERVER_PING_TIMEOUT):
            # Wait until a message is handled
            await asyncio.Future()

    async def handler(self, websocket):
        async for msg in websocket:
            # Parse JSON message to Python dict:
            message = EdgeNetMessage.create_from_json(msg)
            
            # If message is a handshake:
            if message.msg_type == MSG_CONNECTION:
                # Store session
                session = EdgeNetSession.create_from_handshake(msg, websocket)
                self.sessions[message.session_id] = session
