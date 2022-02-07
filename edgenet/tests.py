import unittest, threading

import websockets
from client import EdgeNetClient
from server import EdgeNetServer
from session import EdgeNetSession
from message import EdgeNetMessage
from constants import *


class TestNetwork(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        # Initialize the server + its thread
        self.server_port = 9000
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
        server_url = f"ws://localhost:{self.server_port}"
        client = EdgeNetClient(server_url)
        client.run()

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
        websocket = "DUMMY WEBSOCKET"

        raw_json = f'{{"session_id": "{session_id}", "msg_type": "{msg_type}" }}'
        session = EdgeNetSession.create_from_handshake(raw_json, websocket)

        self.assertIsInstance(session, EdgeNetSession)
        self.assertEqual(session.session_id, session_id)
        self.assertEqual(session.websocket, websocket)
        self.assertEqual(session.status, SESSION_CONNECTED)


if __name__ == "__main__":
    unittest.main()