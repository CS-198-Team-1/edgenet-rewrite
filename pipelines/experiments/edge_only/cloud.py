import threading
from edgenet.server import EdgeNetServer
from config import *
from .functions import *
from .constants import CAPTURE_FPS
from metrics.experiment import Experiment
from metrics.network import NetworkMonitor


for i in range(1,30,1):
    CAPTURE_FPS=i
    PIPELINE = "edge_only"
    EXPERIMENT_ID = f"edge_only{CAPTURE_FPS}"
    NETEM_DELAYS = [
        "100ms", "200ms"
    ]

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
    logging.info("Waiting for five seconds for client to connect...")
    server.sleep(5)

    # Client should be the first in the session dict:
    session_id = [*server.sessions][0]

    # Define a callback function for incoming results:
    def callback(job_result):
        result = job_result.result
        logging.info(f"Received plate {result['plate']} at {result['lat']}, {result['lng']}! Detected at {job_result.sent_dttm} and received at {job_result.recv_dttm}")

    logging.info("Running edge-only execution...")

    if RUN_NETEM_DELAYS:
        for delay in NETEM_DELAYS:
            # Send command to start capturing the video:
            job = server.send_command_external(
                session_id, EDGE_ONLY_FUNCTION_NAME,
                EXPERIMENT_VIDEO_PATH,
                is_polling=True, callback=callback, job_id=f"{EXPERIMENT_ID}_{delay}",
                frames_per_second=CAPTURE_FPS
            )
            # Append job to experiment container
            experiment.jobs.append(job)

            job.wait_until_finished()

            # Wait for metrics transmission
            job.wait_for_metrics()
            job.results_to_csv()
    else:
        # Send command to start capturing the video:
        job = server.send_command_external(
            session_id, EDGE_ONLY_FUNCTION_NAME,
            EXPERIMENT_VIDEO_PATH,
            is_polling=True, callback=callback, job_id=f"{EXPERIMENT_ID}",
            frames_per_second=CAPTURE_FPS
        )
        # Append job to experiment container
        experiment.jobs.append(job)

        job.wait_until_finished()

        # Wait for metrics transmission
        job.wait_for_metrics()
        job.results_to_csv()


    # Stop packet capture
    nmonitor.stop_capturing()

    # Terminate client
    server.send_terminate_external(session_id)

    # Record results
    experiment.end_experiment()
    experiment.to_csv()
    # Get total number of bytes
    #bytes_captured = nmonitor.get_all_packet_size_tcp(SERVER_PORT)
    #logging.info(f"Total bytes captured: {bytes_captured}")
