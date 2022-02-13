import threading, time
from edgenet.server import EdgeNetServer
from config import *
from .functions import *
from metrics.experiment import Experiment

# Initialize experiment
experiment = Experiment("legacy.edge_only")

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

logging.info("Running cloud-only execution...")

rtsp_url = f"{RTSP_URL}/{session_id}"

# Send command to start capturing the video:
job = server.send_command_external(
    session_id, EDGE_FUNCTION_NAME,
    EXPERIMENT_VIDEO_PATH, rtsp_url,
    is_polling=True
)
# Append job to experiment container
experiment.jobs.append(job) # TODO: Figure out how to extract metrics from cloud-only function

time.sleep(1) # TODO: Figure out how to read as soon as stream is published

capture_video(rtsp_url)

# Wait until job is finished, then terminate
# If this is not included, script will terminate immediately!
job.wait_until_finished()
job.wait_for_metrics()

# Terminate client
server.send_terminate_external(session_id)

# Record results
experiment.end_experiment()
experiment.to_csv()