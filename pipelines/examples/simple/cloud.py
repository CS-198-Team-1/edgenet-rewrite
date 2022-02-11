import threading
from edgenet.server import EdgeNetServer
from config import *
from .functions import *

CLOUD_ONLY_TIMES = 10

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

# Call edge-only function ten times:
logging.info(f"Testing edge-only computation to session ID:[{session_id[-12:]}]")
for i in range(10):
    a, b, c = i, i*3, i+23
    logging.info(f"Sending three numbers: {a}, {b}, {c}")
    job = server.send_command_external(
        session_id, EDGE_ONLY_FUNCTION_NAME, 
        a, b, c,
        is_polling=False,
    )
    server.sleep(0.2)
    expected_result = add_three_numbers(a, b, c)
    logging.info(f"Expected result: {expected_result}, received: {job.raw_results[0]}")

# Set up callback for cloud-only computation
def callback(job_result):
    a, b, c = job_result.args
    result = add_three_numbers(a, b, c)
    logging.info(f"Result computed for {(a, b, c)} -> {result}")

# Call cloud-only function, then prcoess it CLOUD_ONLY_TIMES
logging.info(f"Testing cloud-only computation to session ID:[{session_id[-12:]}]")
job = server.send_command_external(
    session_id, CLOUD_ONLY_FUNCTION_NAME,
    CLOUD_ONLY_TIMES,
    is_polling=True, callback=callback
)

job.wait_until_finished()