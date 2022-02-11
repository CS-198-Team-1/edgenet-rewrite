import unittest, threading, time
from unittest.mock import patch, Mock, call
import websockets
from edgenet.client import EdgeNetClient
from edgenet.server import EdgeNetServer
from edgenet.session import EdgeNetSession
from edgenet.message import EdgeNetMessage
from edgenet.constants import *
from metrics.time import uses_timer, Timer, TimerSection


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

        client.run(run_forever=False)
        self.server.sleep(0.1)

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
        self.server.sleep(0.1)

        self.assertTrue(session.websocket.closed)
        self.assertEqual(session.status, SESSION_DISCONNECTED)

    def test_client_handshake(self):
        """
        Tests the client's handshake procedure.
        """
        client = EdgeNetClient(self.server_url)

        # Check if client's connection is still None
        self.assertIsNone(client.connection)

        client.run(run_forever=False)

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
        Tests command called to client
        """
        function_name = "my_special_sum"
        function_method = lambda a, b : a + (b * 2)

        args = [10, 200]
        kwargs = {}
        expected_result = function_method(*args, **kwargs)

        client = EdgeNetClient(self.server_url)
        client.run(run_forever=False)
        client.register_function(function_name, function_method)

        self.server.sleep(0.1)

        job = self.server.send_command_external(
            client.session_id, function_name, is_polling=False,
            *args, **kwargs
        )

        self.server.sleep(0.1)

        self.assertIn(expected_result, job.raw_results)

    def test_server_client_command_finishes(self):
        """
        Tests if awaiting command finishes
        """
        function_name = "my_special_sum"
        function_method = lambda a, b : a + (b * 2)

        args = [10, 200]
        kwargs = {}
        expected_result = function_method(*args, **kwargs)

        client = EdgeNetClient(self.server_url)
        client.run(run_forever=False)
        client.register_function(function_name, function_method)

        self.server.sleep(0.1)

        job = self.server.send_command_external(
            client.session_id, function_name, is_polling=False,
            *args, **kwargs
        )

        self.server.sleep(0.1)

        self.assertIn(expected_result, job.raw_results)
        job.wait_until_finished() # This will not terminate if fails!

    def test_server_client_command_polling(self):
        """
        Tests asynchronous polling commands called to client
        """
        client = EdgeNetClient(self.server_url)
        client.run(run_forever=False)

        function_name = "poll_five_times"

        @client.uses_sender
        def poll_five_times(sender):
            for i in range(3):
                time.sleep(0.1)
                sender.send_result(i)

        client.register_function(function_name, poll_five_times)

        self.server.sleep(0.1)

        job = self.server.send_command_external(
            client.session_id, function_name, is_polling=True
        )

        self.server.sleep(0.5)

        # Check correctness of results
        for i in range(3):
            self.assertIn(i, job.raw_results)

        # Check if threads have closed
        for thread in client.job_threads[job.job_id]:
            self.assertFalse(thread.is_alive())

    def test_server_client_command_polling_finishes(self):
        """
        Tests asynchronous polling commands called to client
        """
        client = EdgeNetClient(self.server_url)
        client.run(run_forever=False)

        function_name = "poll_five_times"

        @client.uses_sender
        def poll_five_times(sender):
            for i in range(3):
                time.sleep(0.1)
                sender.send_result(i)

        client.register_function(function_name, poll_five_times)

        self.server.sleep(0.1)

        job = self.server.send_command_external(
            client.session_id, function_name, is_polling=True
        )

        self.server.sleep(0.5)

        # Check correctness of results
        for i in range(3):
            self.assertIn(i, job.raw_results)

        # Check if threads have closed
        for thread in client.job_threads[job.job_id]:
            self.assertFalse(thread.is_alive())
            
        job.wait_until_finished()

    def test_server_client_command_polling_with_args_kwargs(self):
        """
        Tests asynchronous polling commands called to client (with args and kwargs)
        """
        client = EdgeNetClient(self.server_url)
        client.run(run_forever=False)

        function_name = "poll_five_times"

        args = [623, 123]
        kwargs = {"c": 421, "d": 125}

        expected_results = [
            f"{i} 623 123 421 125" for i in range(3)
        ]

        @client.uses_sender
        def poll_five_times(sender, a, b, c=1, d=2):
            for i in range(3):
                time.sleep(0.1)
                sender.send_result(f"{i} {a} {b} {c} {d}")

        client.register_function(function_name, poll_five_times)

        self.server.sleep(0.1)

        job = self.server.send_command_external(
            client.session_id, function_name, is_polling=True,
            *args, **kwargs
        )

        self.server.sleep(0.5)

        # Check correctness of results
        for result in expected_results:
            self.assertIn(result, job.raw_results)

        # Check if threads have closed
        for thread in client.job_threads[job.job_id]:
            self.assertFalse(thread.is_alive())

    def test_server_client_command_polling_with_multiple_clients(self):
        """
        Tests asynchronous polling commands called to client (with args and kwargs)
        """
        client_1 = EdgeNetClient(self.server_url)
        client_1.run(run_forever=False)
        client_2 = EdgeNetClient(self.server_url)
        client_2.run(run_forever=False)

        function_name = "poll_five_times"

        args_1 = [623, 123]
        kwargs_1 = {"c": 421, "d": 125}
        args_2 = [142437, 48126]
        kwargs_2 = {"c": 9351, "d": 2451}

        expected_results_1 = [
            f"{i} 623 123 421 125" for i in range(3)
        ]
        expected_results_2 = [
            f"{i} 142437 48126 9351 2451" for i in range(3)
        ]

        def poll_five_times(sender, a, b, c=1, d=2):
            for i in range(3):
                time.sleep(0.1)
                sender.send_result(f"{i} {a} {b} {c} {d}")

        client_1.register_function(function_name, client_1.uses_sender(poll_five_times))
        client_2.register_function(function_name, client_2.uses_sender(poll_five_times))

        self.server.sleep(0.1)

        job_1 = self.server.send_command_external(
            client_1.session_id, function_name, is_polling=True,
            *args_1, **kwargs_1
        )

        job_2 = self.server.send_command_external(
            client_2.session_id, function_name, is_polling=True,
            *args_2, **kwargs_2
        )

        self.server.sleep(0.5)

        # Check correctness of results
        for result in expected_results_1:
            self.assertIn(result, job_1.raw_results)
        for result in expected_results_2:
            self.assertIn(result, job_2.raw_results)

        # Check if threads have closed
        for thread in client_1.job_threads[job_1.job_id]:
            self.assertFalse(thread.is_alive())
        for thread in client_2.job_threads[job_2.job_id]:
            self.assertFalse(thread.is_alive())

    def test_server_client_command_callback(self):
        """
        Tests callback function called when result is received
        """

        function_name = "my_special_sum"
        function_method = lambda a, b : a + (b * 2)

        args = [10, 200]
        kwargs = {}
        expected_result = function_method(*args, **kwargs)

        client = EdgeNetClient(self.server_url)
        client.run(run_forever=False)
        client.register_function(function_name, function_method)

        self.server.sleep(0.1)

        callback = Mock()

        job = self.server.send_command_external(
            client.session_id, function_name, is_polling=False,
            callback=callback,
            *args, **kwargs
        )

        self.server.sleep(0.1)

        # Check if callback is called with the result
        callback.assert_called_with(job.results[0])


    def test_server_client_command_polling_callback(self):
        """
        Tests asynchronous polling commands called to client
        """
        client = EdgeNetClient(self.server_url)
        client.run(run_forever=False)

        function_name = "poll_five_times"

        @client.uses_sender
        def poll_five_times(sender):
            for i in range(3):
                time.sleep(0.1)
                sender.send_result(i)

        client.register_function(function_name, poll_five_times)

        self.server.sleep(0.1)

        callback = Mock()

        job = self.server.send_command_external(
            client.session_id, function_name, is_polling=True,
            callback=callback
        )

        self.server.sleep(0.5)

        # Check correctness of results
        for i in range(3):
            self.assertIn(i, job.raw_results)

        # Check if threads have closed
        for thread in client.job_threads[job.job_id]:
            self.assertFalse(thread.is_alive())

        # Check if callback is called with all results:
        callback.assert_has_calls(
            [call(result) for result in job.results]
        )

    def test_server_client_metrics(self):
        """
        Tests asynchronous polling commands called to client (with args and kwargs)
        """
        client = EdgeNetClient(self.server_url)
        client.run(run_forever=False)

        function_name = "poll_five_times"

        args = [623, 123]
        kwargs = {"c": 421, "d": 125}

        expected_results = [
            f"{i} 623 123 421 125" for i in range(3)
        ]

        @client.uses_sender
        @uses_timer
        def poll_five_times(timer, sender, a, b, c=1, d=2):
            timer.start_section("initial-sleep")
            time.sleep(0.1)
            timer.end_section("initial-sleep")
            for i in range(3):
                timer.start_looped_section("looped-sleep")
                time.sleep(0.1)
                sender.send_result(f"{i} {a} {b} {c} {d}")
                timer.end_looped_section("looped-sleep")

            timer.end_function()
            sender.send_metrics(timer)

        client.register_function(function_name, poll_five_times)

        self.server.sleep(0.1)

        job = self.server.send_command_external(
            client.session_id, function_name, is_polling=True,
            *args, **kwargs
        )

        self.server.sleep(0.5)

        # Check correctness of results
        for result in expected_results:
            self.assertIn(result, job.raw_results)

        # Check if threads have closed
        for thread in client.job_threads[job.job_id]:
            self.assertFalse(thread.is_alive())

        # Check if metrics are recorded to job
        self.assertIsInstance(job.metrics, Timer)
        self.assertEqual(job.metrics.function_name, function_name)
        self.assertIsNotNone(job.metrics.call_id)
        self.assertIsInstance(job.metrics.function_time, TimerSection)
        self.assertIsInstance(job.metrics.sections["initial-sleep"], TimerSection)
        for _, section_list in job.metrics.looped_sections.items():
            for section in section_list:
                self.assertIsInstance(section, TimerSection)

        # Check if all metrics are non-zero (should be, anyway)
        self.assertGreater(job.metrics.function_time.elapsed, 0.0)
        for _, section in job.metrics.sections.items():
            self.assertGreater(section.elapsed, 0.0)
        for _, section_list in job.metrics.looped_sections.items():
            for section in section_list:
                self.assertGreater(section.elapsed, 0.0)


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