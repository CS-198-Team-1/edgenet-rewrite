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

# Send command to start capturing the video:
job = server.send_command_external(
    session_id, EDGE_ONLY_FUNCTION_NAME, 
    is_polling=True,
)
