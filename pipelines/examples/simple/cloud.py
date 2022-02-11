import threading
from edgenet.server import EdgeNetServer
from config import *
from .functions import *

# Initialize server
server = EdgeNetServer(SERVER_HOSTNAME, SERVER_PORT)

# Run server
server_thread = threading.Thread(target=server.run, daemon=True)
server_thread.start()

# Wait for 5 seconds for client to connect:
print("Waiting for five seconds for client to connect...")
server.sleep(5)

# Client should be the first in the session dict:
session_id = [*server.sessions][0]

# Call edge-only function ten times:
for i in range(10):
    a, b, c = i, i*3, i+23
    print(f"Sending three numbers: {a}, {b}, {c}")
    job = server.send_command_external(
        session_id, EDGE_ONLY_FUNCTION_NAME, 
        a, b, c,
        is_polling=False,
    )
    server.sleep(0.5)
    expected_result = add_three_numbers(a, b, c)
    print(f"Expected result: {expected_result}, received: {job.raw_results[0]}")
