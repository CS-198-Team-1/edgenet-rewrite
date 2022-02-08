import uuid, asyncio, json
import websockets

from edgenet.constants import MSG_COMMAND
from .message import EdgeNetMessage


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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.perform_handshake())
        loop.create_task(self.handle_commands())

    def close(self):
        async def _close_client():
            await self.connection.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(_close_client())

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

    async def handle_commands(self):
        while True:
            try:
                msg = await self.connection.recv()
            except websockets.ConnectionClosedOK:
                break
            except websockets.ConnectionClosedError:
                break

            message = EdgeNetMessage.create_from_json(msg)

            # If message is a command from the server:
            if message.msg_type == MSG_COMMAND:
                function_call = self.get_function(message.function_name)
                result = function_call(*message.args, **message.kwargs)
                # Create result message
                result_message = EdgeNetMessage.create_result_message(
                    self.session_id, message.job_id, result
                )
                await self.send(result_message)

    async def send(self, message: EdgeNetMessage):
        msg_dict = {
            "session_id": message.session_id,
            "msg_type": message.msg_type
        }
        for e in message.extras:
            msg_dict[e] = getattr(message, e)

        await self.connection.send(json.dumps(msg_dict))

    def get_function(self, function_name):
        return getattr(self, function_name)

    def register_function(self, function_name, function_method):
        setattr(self, function_name, function_method)
        return True
