import logging

# Connection config
SERVER_HOSTNAME          = "localhost"
SERVER_PORT              = 8765
SERVER_GRACE_IN_SECONDS  = 20
EDGE_IDENTIFICATION      = "local"
TERMINATE_CLIENTS_AFTER  = True # Send a termination message after the experiment

# System config
SYSTEM_ARCH = "amd64" # For most Linux servers
# SYSTEM_ARCH = "arm64v8" # For RPi 4

# Edgenet configuration
# -- Kill script through sys.exit() when termination message is received:
#    This is different to TERM..._AFTER, as when set to False, client will still
#    run even though a termination messsage is received.
# -- Note: this is overriden by test.py in order to do tests gracefully
TERMINATE_CLIENTS_ON_RECEIVE = True

# Experiment configuration
# -- Video and GPX information
EXPERIMENT_VIDEO_PATH = "experiment-files/test_video_4.mp4"
GPX_PATH = "experiment-files/exp_1.gpx"
VIDEO_WIDTH     = 1920
VIDEO_HEIGHT    = 1080
VIDEO_FPS       = 30
BASE_CONFIDENCE = 0.3
# -- Variables and constraints
REPEATS        = 2
CAPTURE_FPS    = 2
BW_CONSTRAINT  = None # Set to None to remove constraint

# Streaming config
RTSP_PORT = 8554 # See rtsp-simple-server.yml:107 to change RTMP port as well.
RTSP_URL = f"rtsp://{SERVER_HOSTNAME}:{RTSP_PORT}"

# Network metrics config
NET_INTERFACE = "eth0"

# Logging config
LOGGING_LEVEL       = logging.INFO
LOGGING_FORMAT      = "[%(asctime)s] %(levelname)-8s %(message)s"
LOGGING_DATEFMT     = "%y-%m-%d %H:%M:%S"

# Logging setup
logging.basicConfig(
    level=LOGGING_LEVEL,
    format=LOGGING_FORMAT,
    datefmt=LOGGING_DATEFMT
)
