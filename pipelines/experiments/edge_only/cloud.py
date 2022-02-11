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
logging.info("Waiting for five seconds for client to connect...")
server.sleep(5)

# Client should be the first in the session dict:
session_id = [*server.sessions][0]

# Define a callback function for incoming results:
def callback(job_result):
    result = job_result.result
    logging.info(f"Received plate {result['plate']} at {result['lat']}, {result['lng']}! Detected at {job_result.sent_dttm} and received at {job_result.recv_dttm}")

logging.info("Running edge-only execution...")
# Send command to start capturing the video:
job = server.send_command_external(
    session_id, EDGE_ONLY_FUNCTION_NAME,
    EXPERIMENT_VIDEO_PATH,
    is_polling=True, callback=callback
)

# Wait until job is finished, then terminate
# If this is not included, script will terminate immediately!
job.wait_until_finished()
