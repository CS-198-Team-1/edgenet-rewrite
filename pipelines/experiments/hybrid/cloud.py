import threading, subprocess
from .constants import *
from edgenet.server import EdgeNetServer
from config import *
from .functions import *
from metrics.experiment import Experiment
from metrics.network import NetworkMonitor
from metrics.time import Timer
from datetime import datetime
from gpx import parser
from dateutil import parser as dttm_parser

PIPELINE = "hybrid"
EXPERIMENT_ID = f"hybrid_{CAPTURE_FPS}"

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
logging.info(f"Waiting for {SERVER_GRACE_IN_SECONDS} seconds for client to connect...")
server.sleep(SERVER_GRACE_IN_SECONDS)

# Initialize experiment and bandwidth monitoring after sleep
experiment = Experiment(PIPELINE, experiment_id=EXPERIMENT_ID)
nmonitor = NetworkMonitor("lo", experiment.experiment_id)
nmonitor.start_capturing()

# Get all connected sessions:
session_ids = [*server.sessions]
# -- Quickly modify experiment ID to match session count
experiment.experiment_id = f"{experiment.experiment_id}_{len(session_ids)}"

logging.info("Running hybridized execution...")

rtsp_url = f"{RTSP_URL}/{session_id}"

# # Start capturing the stream
# r_list = []
# cap_thread = threading.Thread(target=capture_video, args=[rtsp_url], kwargs={"results_list": r_list})
# cap_thread.start()

# Implement rate constraint
# nmonitor.implement_rate("256kbit")

gpxc = None

for iteration in range(REPEATS):

    pending_jobs_and_cloud_metrics = []

    for session_id in session_ids:
        iteration_id = f"{session_id}_I{iteration}"
        
        cloud_metrics = Timer(f"cloud_metrics_{session_id}")

        # Callback to recognize plate:
        def callback(job_result):
            global gpxc

            result = job_result.result

            # Sync GPX
            if gpxc is None:
                start_time = dttm_parser.parse(result["start_time"]).replace(tzinfo=None)
                gpxc = parser.parse_gpx_and_sync(GPX_PATH, start_time)
            
            # Remove "start_time"
            del job_result.result["start_time"]

            cloud_metrics.start_looped_section("cloud-recognition")
            plate_detected, plate_text, lat, lng, conf, r, n = execute_text_recognition_tflite(**result, gpxc=gpxc)
            cloud_metrics.end_looped_section("cloud-recognition")
            
            if plate_detected:
                logging.info(f"Recognized plate {plate_text} at {lat}, {lng}! Detected at {job_result.sent_dttm} and recognized at {datetime.now().isoformat()}")

            # Modify results for .csv:
            del job_result.result["cropped_frame"]
            job_result.result["time_captured"] = r
            job_result.result["time_now"]      = n
            job_result.result["plate"]         = plate_text
            job_result.result["lat"]           = lat
            job_result.result["lng"]           = lng

        # Send command to start detecting the video:
        job = server.send_command_external(
            session_id, EDGE_FUNCTION_NAME,
            EXPERIMENT_VIDEO_PATH, 
            is_polling=True, job_id=f"{experiment.experiment_id}_{iteration_id}",
            callback=callback,
            frames_per_second=CAPTURE_FPS
        )

        # Append job to experiment container
        experiment.jobs.append(job) # TODO: Figure out how to extract metrics from cloud-only function

        # Append to pending as a tuple
        pending_jobs_and_cloud_metrics.append((job, cloud_metrics))

    for job, cloud_metrics in pending_jobs_and_cloud_metrics:
        # Wait until job is finished
        job.wait_until_finished()

        # Wait for edge-side metrics
        job.wait_for_metrics()

        # Register cloud metrics
        cloud_metrics.end_function()
        job.register_metrics(cloud_metrics)

        # Finally, save as CSV
        job.results_to_csv()


# Release rate constraint
# nmonitor.release_rate()

# # Get results from the cloud side, and delete pickle
# cloud_metrics = Timer.wait_for_and_consume_pickle("legacy-cloud-only.pickle")

# Clean up
# cap_thread.join()
rtsp_server.terminate()
server.send_terminate_external(session_id)

# Record results
experiment.end_experiment()
nmonitor.stop_capturing()
experiment.to_csv()

# Display bandwidth usage
websocket_usage = nmonitor.get_all_packet_size_tcp(SERVER_PORT)
rtsp_usage = nmonitor.get_all_packet_size_tcp(RTSP_PORT)

logging.info(f"Total bytes through websockets: {websocket_usage}")
logging.info(f"Total bytes through RTSP: {rtsp_usage}")
