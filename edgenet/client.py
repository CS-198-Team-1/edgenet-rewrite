import uuid, asyncio, json, threading, os
import websockets

from edgenet.constants import *
from .message import EdgeNetMessage
from config import *

class EdgeNetClient:
    def __init__(
        self, server_url, session_id=None, 
        terminate_on_receive=TERMINATE_CLIENTS_ON_RECEIVE
    ):
        self.server_url           = server_url
        self.terminate_on_receive = terminate_on_receive

        # Generate a random UUID if not given
        if session_id is None:
            self.session_id = str(uuid.uuid4())
        else:
            self.session_id = session_id

        # Connection is initially null
        self.connection = None

        # Collection of open threads to be cleaned up
        self.job_threads = {}
        
        logging.info(f"EdgeNetClient for host {server_url} instantiated with session ID {self.session_id[-12:]}")

    def run(self, run_forever=True):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.perform_handshake())
        loop.create_task(self.handle_commands())
        
        if run_forever: loop.run_forever()

    async def _close(self):
        await self.connection.close()

    def close(self, close_forever=False):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._close())
        
        # Only set close_forever to True if no clients will be spawned again
        # in the same thread
        if close_forever: 
            loop.close()

    async def perform_handshake(self):
        backoff_time = INITIAL_BACKOFF_TIME_IN_SECONDS
        while True:
            try:
                self.connection = await websockets.connect(self.server_url)
                break
            except ConnectionRefusedError:
                pass
            # Exponential backoff
            logging.info(f"Failed to connect to server, trying again in {backoff_time} seconds.")
            await asyncio.sleep(backoff_time)
            backoff_time = min( 2*backoff_time, MAX_BACKOFF_TIME_IN_SECONDS )

        handshake_message = EdgeNetMessage.create_client_handshake_message(self.session_id)
        
        await self.send(handshake_message)
        logging.info(f"Connection to server established.")

    async def handle_commands(self):
        while True:
            try:
                msg = await self.connection.recv()
            except websockets.ConnectionClosedOK:
                break
            except websockets.ConnectionClosedError:
                break

            logging.debug("Message received from server!")
            message = EdgeNetMessage.create_from_json(msg)

            # If message is a command from the server:
            if message.msg_type == MSG_COMMAND:
                logging.debug(f"Message is of COMMAND type, running function with name [{message.function_name}] with job ID:[{message.job_id[-12:]}]")

                function_call = self.get_function(message.function_name)
                result = function_call(*message.args, **message.kwargs)
                
                logging.debug(f"Function call for job ID:[{message.job_id[-12:]}] completed, sending the result...")
                
                # Create result message
                result_message = EdgeNetMessage.create_result_message(
                    self.session_id, message.job_id, result
                )
                await self.send(result_message)
                
                logging.debug(f"Result message sent! Now sending FINISH message for job ID:{message.job_id[-12:]}...")
                
                await self.send_job_finished(message.job_id)

                logging.debug(f"FINISH message sent for job ID:[{message.job_id[-12:]}]!")
            
            # If message is a polling command
            if message.msg_type == MSG_COMMAND_POLL:
                function_call = self.get_function(message.function_name)
                result = function_call(message, *message.args, **message.kwargs)
                await self.send_job_finished(message.job_id)

            if message.msg_type == MSG_TERMINATE:
                await self._close()
                if self.terminate_on_receive:
                    os.kill(os.getpid(), 9)

    async def send(self, message: EdgeNetMessage):
        msg_dict = {
            "session_id": message.session_id,
            "msg_type": message.msg_type
        }
        for e in message.extras:
            msg_dict[e] = getattr(message, e)

        await self.connection.send(json.dumps(msg_dict))

    async def send_job_finished(self, job_id):
        await self.send(EdgeNetMessage.create_job_finished_message(
            self.session_id, job_id
        ))

    def get_function(self, function_name):
        return getattr(self, function_name)

    def register_function(self, function_name, function_method):
        setattr(self, function_name, function_method)
        logging.debug(f"Function registered with name [{function_name}].")
        return True

    def uses_sender(self, func):
        def wrapper(message, *args, **kwargs):
            # Asyncio caller for sending results
            def _send_result(result):
                result_message = EdgeNetMessage.create_result_message(
                    self.session_id, message.job_id, result
                )

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                loop.run_until_complete(self.send(result_message))
                loop.close()

            # Thread starter for the caller above, for concurrency
            def send_result(result):
                _thread = threading.Thread(target=_send_result, args=[result])
                _thread.start()
                self.job_threads[message.job_id].append(_thread)
                logging.debug("Timer metrics successfully sent to server.")

            # Asyncio caller for sending results
            def _send_metrics(timer_object):
                metrics_message = EdgeNetMessage.create_metrics_message(
                    self.session_id, message.job_id, timer_object # Transform to dict
                )

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                loop.run_until_complete(self.send(metrics_message))
                loop.close()
                logging.info(f"Metrics for {timer_object.call_id[-12:]} successfully sent to server.")

            # Thread starter for the caller above, for concurrency
            def send_metrics(timer_object):
                _thread = threading.Thread(target=_send_metrics, args=[timer_object])
                _thread.start()
                self.job_threads[message.job_id].append(_thread)

            # Make a generic class
            class Sender: pass

            # Assign sender functions
            sender = Sender()
            sender.send_result  = send_result
            sender.send_metrics = send_metrics

            # Initialize job thread list
            self.job_threads[message.job_id] = []

            result = func(sender, *args, **kwargs)

            # Cleanup for all the job threads
            for thread in self.job_threads[message.job_id]:
                thread.join()

            return result

        return wrapper
