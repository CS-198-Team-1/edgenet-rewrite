import threading
from edgenet.server import EdgeNetServer
from config import *
from .functions import *
from .constants import CAPTURE_FPS
from metrics.experiment import Experiment
from metrics.network import NetworkMonitor

PIPELINE = "edge_only"
EXPERIMENT_ID = f"edge_only{CAPTURE_FPS}"

# Initialize experiment
experiment = Experiment(PIPELINE, experiment_id=EXPERIMENT_ID)

# Initialize network monitor
nmonitor = NetworkMonitor(NET_INTERFACE, experiment_id=experiment.experiment_id)

# Initialize server
server = EdgeNetServer("0.0.0.0", SERVER_PORT)

# Start packet capture
nmonitor.start_capturing()

# Run server
server_thread = threading.Thread(target=server.run, daemon=True)
server_thread.start()

# Wait for 5 seconds for client to connect:
logging.info(f"Waiting for {SERVER_GRACE_IN_SECONDS} seconds for client to connect...")
server.sleep(SERVER_GRACE_IN_SECONDS)

# Get all connected sessions:
session_ids = [*server.sessions]

# Define a callback function for incoming results:
def callback(job_result):
    result = job_result.result
    logging.info(f"Received plate {result['plate']} at {result['lat']}, {result['lng']}! Detected at {job_result.sent_dttm} and received at {job_result.recv_dttm}")

logging.info("Running edge-only execution...")

# Send commands to start capturing the video:
pending_jobs = []
for session_id in session_ids:
    job = server.send_command_external(
        session_id, EDGE_ONLY_FUNCTION_NAME,
        EXPERIMENT_VIDEO_PATH,
        is_polling=True, callback=callback, job_id=f"{EXPERIMENT_ID}",
        frames_per_second=CAPTURE_FPS
    )
    # Append jobs containers
    pending_jobs.append(job)
    experiment.jobs.append(job)

for job in pending_jobs:
    # Wait for job to finish:
    job.wait_until_finished()
    # Wait for metrics transmission
    job.wait_for_metrics()
    job.results_to_csv()

# Stop packet capture
nmonitor.stop_capturing()

# Terminate clients if config is set to yes
if TERMINATE_CLIENTS_AFTER:
    for session_id in session_ids:
        server.send_terminate_external(session_id)

# Record results
experiment.end_experiment()
experiment.to_csv()
# Get total number of bytes
bytes_captured = nmonitor.get_all_packet_size_tcp(SERVER_PORT)
logging.info(f"Total bytes captured: {bytes_captured}")
