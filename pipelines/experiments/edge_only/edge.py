from edgenet.client import EdgeNetClient, EdgeNetMessage
from gpx import uses_gpx
from config import *
from .functions import *

# Initialize client
client = EdgeNetClient(f"ws://{SERVER_HOSTNAME}:{SERVER_PORT}")

# Use decorator
edge_only_video_capture = client.uses_sender(capture_video)

# Register functions
client.register_function(EDGE_ONLY_FUNCTION_NAME, edge_only_video_capture)

# Run client
client.run()
