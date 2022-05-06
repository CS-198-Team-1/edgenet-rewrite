from edgenet.client import EdgeNetClient, EdgeNetMessage
from gpx import uses_gpx
from config import *
from .functions import *
from argparse import ArgumentParser as ArgParser

# Parse arguments
_parser = ArgParser(description="Execute the hybrid pipeline.")
_parser.add_argument("--port", type=str, dest="SERVER_PORT", default=SERVER_PORT)

_args = _parser.parse_args()

# Override config
SERVER_PORT   = _args.SERVER_PORT

# Initialize client
client = EdgeNetClient(f"ws://{SERVER_HOSTNAME}:{SERVER_PORT}", session_id=EDGE_IDENTIFICATION)

# Use decorator
edge_only_video_capture = client.uses_sender(capture_video)

# Register functions
client.register_function(EDGE_ONLY_FUNCTION_NAME, edge_only_video_capture)

# Run client
client.run()
