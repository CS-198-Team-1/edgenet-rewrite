import threading, subprocess
from edgenet.server import EdgeNetServer
from config import *
from .functions import *
from metrics.experiment import Experiment

# Initialize server
server = EdgeNetServer("0.0.0.0", SERVER_PORT)

# Start RTSP server
rtsp_server = subprocess.Popen(
    [f"./bin/{SYSTEM_ARCH}/rtsp-simple-server"], 
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# Run server
server_thread = threading.Thread(target=server.run, daemon=True)
server_thread.start()

# Wait for 5 seconds for client to connect:
logging.info("Waiting for five seconds for client to connect...")
server.sleep(5)

# Initialize experiment after sleep
experiment = Experiment("legacy.edge_only")

# Client should be the first in the session dict:
session_id = [*server.sessions][0]

logging.info("Running cloud-only execution...")

rtsp_url = f"{RTSP_URL}/{session_id}"

# Start capturing the stream
r_list = []
cap_thread = threading.Thread(target=capture_video, args=[rtsp_url], kwargs={"results_list": r_list})
cap_thread.start()

# Send command to start publishing the video:
job = server.send_command_external(
    session_id, EDGE_FUNCTION_NAME,
    EXPERIMENT_VIDEO_PATH, rtsp_url,
    is_polling=True
)

# Append job to experiment container
experiment.jobs.append(job) # TODO: Figure out how to extract metrics from cloud-only function

# Wait until job is finished, then terminate
job.wait_until_finished()
job.wait_for_metrics()

# Get results from the cloud side, and delete pickle
cloud_metrics = Timer.wait_for_and_consume_pickle("legacy-cloud-only.pickle")

# Add cloud metrics and results
job.register_metrics(cloud_metrics)
job.results = r_list

# Record results
experiment.end_experiment()
experiment.to_csv()
job.results_to_csv()

# Clean up
cap_thread.join()
rtsp_server.terminate()
server.send_terminate_external(session_id)
