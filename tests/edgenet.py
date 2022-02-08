import unittest, threading, time, asyncio
from unittest.mock import patch
import websockets
from edgenet.client import EdgeNetClient
from edgenet.server import EdgeNetServer
from edgenet.session import EdgeNetSession
from edgenet.message import EdgeNetMessage
from edgenet.constants import *


class TestNetwork(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        # Initialize the server + its thread
        self.server_ip = "localhost"
        self.server_port = 9000
        self.server_url = f"ws://{self.server_ip}:{self.server_port}"
        self.server = EdgeNetServer("localhost", self.server_port)
        self.server_thread = threading.Thread(target=self.server.run, daemon=True)
        self.server_thread.start()

    @classmethod
    def tearDownClass(self):
        super().tearDownClass()

    def test_server_handshake(self):
        """
        Tests the server's handshake procedure.
        """
        client = EdgeNetClient(self.server_url)

        # Check if session_id is NOT YET in server's sessions dict
        self.assertNotIn(client.session_id, self.server.sessions)

        client.run()
        self.server.sleep(1)

        # Check if session_id is in server's sessions dict
        self.assertIn(client.session_id, self.server.sessions)

        # Fetch session and check attributes
        session = self.server.sessions[client.session_id]
        self.assertEqual(session.session_id, client.session_id)
        self.assertEqual(session.status, SESSION_CONNECTED)
        self.assertIsInstance(
            session.websocket, 
            websockets.legacy.server.WebSocketServerProtocol
        )

        self.assertTrue(session.websocket.open)

        client.close()
        self.server.sleep(1)

        self.assertTrue(session.websocket.closed)
        self.assertEqual(session.status, SESSION_DISCONNECTED)


    def test_client_handshake(self):
        """
        Tests the client's handshake procedure.
        """
        client = EdgeNetClient(self.server_url)

        # Check if client's connection is still None
        self.assertIsNone(client.connection)

        client.run()

        # Check if client properly stored the connection
        self.assertIsInstance(
            client.connection, 
            websockets.legacy.client.WebSocketClientProtocol
        )
        self.assertTrue(client.connection.open)

        client.close()

        self.assertTrue(client.connection.closed)

    def test_server_client_command(self):
        """
        Tests command calling to client
        """
        function_name = "my_special_sum"
        function_method = lambda a, b : a + (b * 2)

        args = [10, 200]
        kwargs = {}
        expected_result = function_method(*args, **kwargs)

        client = EdgeNetClient(self.server_url)
        client.run()
        client.register_function(function_name, function_method)

        self.server.sleep(1)

        # asyncio.run(self.server.send_command(client.session_id, function_name, *args, **kwargs))

        job = self.server.send_command_external(client.session_id, function_name, *args, **kwargs)

        self.server.sleep(1)

        self.assertIn(expected_result, job.raw_results)


class TestMessage(unittest.TestCase):
    def test_message_create_from_json(self):
        """
        Tests the create_from_json class method.
        """
        session_id = "abcdef"
        msg_type = MSG_CONNECTION

        raw_json = f'{{"session_id": "{session_id}", "msg_type": "{msg_type}" }}'
        message = EdgeNetMessage.create_from_json(raw_json)

        self.assertIsInstance(message, EdgeNetMessage)
        self.assertEqual(message.session_id, session_id)
        self.assertEqual(message.msg_type, msg_type)


class TestSession(unittest.TestCase):
    def test_session_create_from_handshake(self):
        """
        Tests the create_from_handshake class method.
        """
        session_id = "abcdef"
        msg_type = MSG_CONNECTION

        # Mock websocket object 
        with patch("websockets.legacy.server.WebSocketServerProtocol") as ws:
            ws.return_value.open = True

        raw_json = f'{{"session_id": "{session_id}", "msg_type": "{msg_type}" }}'
        session = EdgeNetSession.create_from_handshake(raw_json, ws)

        self.assertIsInstance(session, EdgeNetSession)
        self.assertEqual(session.session_id, session_id)
        self.assertEqual(session.websocket, ws)
        self.assertEqual(session.status, SESSION_CONNECTED)


if __name__ == "__main__":
    unittest.main()