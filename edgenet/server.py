import asyncio, uuid, json
import websockets
from .session import EdgeNetSession
from .message import EdgeNetMessage
from .job import EdgeNetJob, EdgeNetJobResult
from .constants import *


class EdgeNetServer:
    def __init__(self, hostname, port):
        self.hostname   = hostname
        self.port       = port
        self.is_running = True

        # Set empty dict to store sessions
        self.sessions = {}
        self.jobs     = {}

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.serve())

    def send_command_external(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.send_command(*args, **kwargs))

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

            if message.msg_type == MSG_RESULT:
                self.jobs[message.job_id].register_result_from_message(message)

    async def send_message(self, session_id, message: EdgeNetMessage):
        msg_dict = {
            "session_id": message.session_id,
            "msg_type": message.msg_type
        }
        for e in message.extras:
            msg_dict[e] = getattr(message, e)

        await self.sessions[session_id].websocket.send(json.dumps(msg_dict))

    async def send_command(self, session_id, function_name, *args, **kwargs):
        # Initialize a job object
        job = EdgeNetJob(str(uuid.uuid4()), function_name, args, kwargs)
        self.jobs[job.job_id] = job

        # Create the command message and send it
        command_message = job.create_command_message(session_id)
        await self.send_message(session_id, command_message)

        # Return the job object
        return job

    def sleep(self, seconds):
        # Sleep call used for testing
        async def _sleep():
            await asyncio.sleep(seconds)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(_sleep())
        
