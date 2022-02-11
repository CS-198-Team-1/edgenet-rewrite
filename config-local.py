import logging

# Connection config
SERVER_HOSTNAME     = "localhost"
SERVER_PORT         = 8765

# System config
SYSTEM_ARCH = "amd64" # For most Linux servers
# SYSTEM_ARCH = "arm64v8" # For RPi 4

# Streaming config
RTSP_PORT = 8554 # See rtsp-simple-server.yml:107 to change RTMP port as well.
RTSP_URL = f"rtsp://{SERVER_HOSTNAME}:{RTSP_PORT}"

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
