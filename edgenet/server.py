import asyncio, uuid, json
import websockets
from metrics.time import Timer
from .session import EdgeNetSession
from .message import EdgeNetMessage
from .job import EdgeNetJob, EdgeNetJobResult
from .constants import *
from config import *


class EdgeNetServer:
    def __init__(self, hostname, port):
        self.hostname   = hostname
        self.port       = port
        self.is_running = True

        # Set empty dict to store sessions
        self.sessions = {}
        self.jobs     = {}

        logging.debug(f"EdgeNetServer for host {hostname}:{port} instantiated.")

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.serve())

    def send_command_external(
        self, session_id, function_name, *args, 
        is_polling=False, callback=None,
        **kwargs
    ):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.send_command(
            session_id, function_name, is_polling=is_polling,
            callback=callback,
            *args, **kwargs
        ))

        return result

    def send_terminate_external(self, session_id):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.send_terminate(session_id))

        return result

    async def serve(self, stop=asyncio.Future()):
        # Main server loop
        async with websockets.serve(self.handler, self.hostname, self.port, ping_timeout=SERVER_PING_TIMEOUT):
            # Wait until a message is handled
            await asyncio.Future()

    async def handler(self, websocket):
        async for msg in websocket:
            # Parse JSON message to Python dict:
            message = EdgeNetMessage.create_from_json(msg)
            logging.debug(f"Message received from session ID:[{message.session_id[-12:]}]")

            # If message is a handshake:
            if message.msg_type == MSG_CONNECTION:
                # Store session
                session = EdgeNetSession.create_from_handshake(msg, websocket)
                self.sessions[message.session_id] = session
                logging.debug(f"Message was of CONNECTION type, successfully registered session ID:[{message.session_id[-12:]}].")

            # If message is a job result
            if message.msg_type == MSG_RESULT:
                logging.debug(f"Message was of RESULT type for job ID:[{message.job_id[-12:]}].")
                self.jobs[message.job_id].register_result_from_message(message)

            # If message indicates that a job is finished
            if message.msg_type == MSG_FINISH:
                logging.debug(f"Message was of FINISH type for job ID:[{message.job_id[-12:]}].")
                self.jobs[message.job_id].finish_job()

            # If message contains metrics data
            if message.msg_type == MSG_METRICS:
                # Register Timer object to our job
                timer_obj = Timer.create_from_dict(message.metrics)
                self.jobs[message.job_id].register_metrics(timer_obj)

    async def send_message(self, session_id, message: EdgeNetMessage):
        msg_dict = {
            "session_id": message.session_id,
            "msg_type": message.msg_type
        }
        for e in message.extras:
            msg_dict[e] = getattr(message, e)

        await self.sessions[session_id].websocket.send(json.dumps(msg_dict))

    async def send_command(
        self, session_id, function_name, *args, 
        is_polling=False, callback=None,
        **kwargs
        ):
        # Initialize a job object
        job = EdgeNetJob(
            str(uuid.uuid4()), function_name, args=args, kwargs=kwargs,
            callback=callback
        )
        self.jobs[job.job_id] = job

        logging.debug(f"EdgeNetJob instantiated with job ID:[{job.job_id[-12:]}], with args:{args} and kwargs={kwargs}")

        # Create the command message and send it
        command_message = job.create_command_message(session_id, is_polling=is_polling)
        await self.send_message(session_id, command_message)

        logging.debug(f"Job command message for job ID:[{job.job_id[-12:]}] has been sent.")

        # Return the job object
        return job

    async def send_terminate(self, session_id):
        # Create the termination message and send it
        term_message = EdgeNetMessage.create_terminate_message(session_id)
        await self.send_message(session_id, term_message)

        logging.debug(f"Terminate message for session ID:[{session_id[-12:]}] has been sent.")

        self.sessions[session_id].terminate()

        return self.sessions[session_id]

    def sleep(self, seconds):
        # Sleep call used for testing
        async def _sleep():
            await asyncio.sleep(seconds)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(_sleep())
        
