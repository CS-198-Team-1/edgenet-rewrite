import threading, subprocess
from .constants import *
from edgenet.server import EdgeNetServer
from config import *
from .functions import *
from metrics.experiment import Experiment
from metrics.network import NetworkMonitor

PIPELINE = "cloud-heavy"

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

# Get all connected sessions:
session_ids = [*server.sessions]
# -- Initialize experiment with formatted name:
experiment_id = "_".join( map(str, [
    PIPELINE, CAPTURE_FPS, 
    len(session_ids), # Num. of edge instances
    BW_CONSTRAINT,
    ]) )
experiment = Experiment(PIPELINE, experiment_id=experiment_id)

logging.info("Running cloud-only execution...")

# Repeat REPEATS times:
for iteration in range(REPEATS):
    # -- Start capture
    nmonitor = NetworkMonitor(NET_INTERFACE, f"{experiment.experiment_id}_I{iteration}")
    nmonitor.start_capturing()

    # Implement constraint if it exists
    if BW_CONSTRAINT:
        nmonitor.implement_rate(BW_CONSTRAINT)

    pending_threads = []
    pending_jobs = []

    for session_id in session_ids:
        iteration_id = f"{session_id}_I{iteration}"
        rtsp_url = f"{RTSP_URL}/{session_id}"

        # Send command to start publishing the video:
        job = server.send_command_external(
            session_id, EDGE_FUNCTION_NAME,
            EXPERIMENT_VIDEO_PATH, rtsp_url,
            is_polling=True, job_id=f"{experiment.experiment_id}_{iteration_id}"
        )

        def job_with_metrics(_job):
            metrics, _ = capture_video(
                f"rtsp://0.0.0.0:8554/{session_id}", 
                frames_per_second=CAPTURE_FPS,
                results_list=_job.results)
            # Automatically attach metrics after it is done
            _job.register_metrics(metrics)

        cloud_metrics = None
        capture_thread = threading.Thread(target=job_with_metrics, args=[job,])
        capture_thread.start()

        # Append job to experiment container
        experiment.jobs.append(job)

        # Append to pending
        pending_jobs.append(job)
        pending_threads.append(capture_thread)

    for thread in pending_threads:
        thread.join()
        logging.info(f"Capture thread successfully joined.")

    for job in pending_jobs:
        # Wait until job is finished
        job.wait_until_finished()
        job.wait_for_metrics(number_of_metrics=2) # Since we have cloud-side metrics too
        job.results_to_csv()
    
    # Release constraint if it exists
    if BW_CONSTRAINT:
        nmonitor.release_rate()

    # Stop packet capture
    nmonitor.stop_capturing()
        
# Clean up
rtsp_server.terminate()

# Terminate clients if config is set to yes
if TERMINATE_CLIENTS_AFTER:
    for session_id in session_ids:
        server.send_terminate_external(session_id)

# Record results
experiment.end_experiment()
experiment.to_csv()
