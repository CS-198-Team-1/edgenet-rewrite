from edgenet.client import EdgeNetClient, EdgeNetMessage
from gpx import uses_gpx
from config import *
from .functions import start_streaming

# Initialize client
client = EdgeNetClient(f"ws://{SERVER_HOSTNAME}:{SERVER_PORT}")

# Use decorator
edge_video_stream = client.uses_sender(start_streaming)

# Register functions
client.register_function(EDGE_FUNCTION_NAME, edge_video_stream)

# Run client
client.run()
