import logging

SERVER_HOSTNAME     = "localhost"
SERVER_PORT         = 8765

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
