import threading, subprocess
from .constants import *
from edgenet.server import EdgeNetServer
from config import *
from .functions import *
from metrics.experiment import Experiment
from metrics.network import NetworkMonitor

PIPELINE = "cloud_only"
RATE_CONSTRAINT = "1Mbit"
EXPERIMENT_ID = f"cloud_only_{RATE_CONSTRAINT}"

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

# Initialize experiment and bandwidth monitoring after sleep
experiment = Experiment(PIPELINE, experiment_id=EXPERIMENT_ID)
nmonitor = NetworkMonitor(NET_INTERFACE, experiment.experiment_id)
nmonitor.start_capturing()

# Client should be the first in the session dict:
session_id = [*server.sessions][0]

logging.info("Running cloud-only execution...")

rtsp_url = f"{RTSP_URL}/{session_id}"

# # Start capturing the stream
# r_list = []
# cap_thread = threading.Thread(target=capture_video, args=[rtsp_url], kwargs={"results_list": r_list})
# cap_thread.start()

# Implement rate constraint
nmonitor.implement_rate(RATE_CONSTRAINT)

# Send command to start publishing the video:
job = server.send_command_external(
    session_id, EDGE_FUNCTION_NAME,
    EXPERIMENT_VIDEO_PATH, rtsp_url,
    is_polling=True, job_id=EXPERIMENT_ID
)

cloud_metrics, job.results = capture_video(f"rtsp://0.0.0.0:8554/{session_id}", frames_per_second=CAPTURE_FPS)

# Append job to experiment container
experiment.jobs.append(job) # TODO: Figure out how to extract metrics from cloud-only function

# Wait until job is finished, then terminate
job.wait_until_finished()
job.wait_for_metrics()

# Release rate constraint
nmonitor.release_rate()

# # Get results from the cloud side, and delete pickle
# cloud_metrics = Timer.wait_for_and_consume_pickle("legacy-cloud-only.pickle")

# Add cloud metrics and results
job.register_metrics(cloud_metrics)
# job.results = r_list

# Clean up
# cap_thread.join()
rtsp_server.terminate()
server.send_terminate_external(session_id)

# Record results
experiment.end_experiment()
nmonitor.stop_capturing()
experiment.to_csv()
job.results_to_csv()

# Display bandwidth usage
websocket_usage = nmonitor.get_all_packet_size_tcp(SERVER_PORT)
rtsp_usage = nmonitor.get_all_packet_size_tcp(RTSP_PORT)

logging.info(f"Total bytes through websockets: {websocket_usage}")
logging.info(f"Total bytes through RTSP: {rtsp_usage}")
