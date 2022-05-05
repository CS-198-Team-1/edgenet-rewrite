import threading
from edgenet.server import EdgeNetServer
from config import *
from .functions import *
from metrics.experiment import Experiment
from metrics.network import NetworkMonitor

PIPELINE = "edge-heavy"

# Initialize server
server = EdgeNetServer("0.0.0.0", SERVER_PORT)

# Run server
server_thread = threading.Thread(target=server.run, daemon=True)
server_thread.start()

# Wait for 5 seconds for client to connect:
logging.info(f"Waiting for {SERVER_GRACE_IN_SECONDS} seconds for client to connect...")
server.sleep(SERVER_GRACE_IN_SECONDS)

# Get all connected sessions:
session_ids = [*server.sessions]
# -- Quickly modify experiment ID to match session count
# -- Initialize experiment with formatted name:
experiment_id = "_".join( map(str, [
    PIPELINE, CAPTURE_FPS, 
    len(session_ids), # Num. of edge instances
    BW_CONSTRAINT,
    ]) )
experiment = Experiment(PIPELINE, experiment_id=experiment_id)

# Define a callback function for incoming results:
def callback(job_result):
    result = job_result.result
    logging.info(f"Received plate {result['plate']} at {result['lat']}, {result['lng']}! Detected at {job_result.sent_dttm} and received at {job_result.recv_dttm}")

logging.info("Running edge-only execution...")

for iteration in range(REPEATS):
    # -- Start capture
    nmonitor = NetworkMonitor(NET_INTERFACE, f"{experiment.experiment_id}_I{iteration}")
    nmonitor.start_capturing()

    # Implement constraint if it exists
    if BW_CONSTRAINT:
        nmonitor.implement_rate(BW_CONSTRAINT)

    pending_jobs = []

    for session_id in session_ids:
        iteration_id = f"{session_id}_I{iteration}"
        job = server.send_command_external(
            session_id, EDGE_ONLY_FUNCTION_NAME,
            EXPERIMENT_VIDEO_PATH,
            is_polling=True, callback=callback, job_id=f"{experiment.experiment_id}_{iteration_id}",
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

    # Release constraint if it exists
    if BW_CONSTRAINT:
        nmonitor.release_rate()

    # Stop packet capture
    nmonitor.stop_capturing()

# Terminate clients if config is set to yes
if TERMINATE_CLIENTS_AFTER:
    for session_id in session_ids:
        server.send_terminate_external(session_id)

# Record results
experiment.end_experiment()
experiment.to_csv()
