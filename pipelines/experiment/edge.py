from edgenet.client import EdgeNetClient, EdgeNetMessage
from gpx import uses_gpx
from config import *
from .functions import *

# Initialize client
client = EdgeNetClient(f"ws://{SERVER_HOSTNAME}:{SERVER_PORT}")

# Register functions
edge_only_video_capture = client.uses_sender(capture_video)

mock_message = EdgeNetMessage("1", "1", job_id="2")

edge_only_video_capture(mock_message, "experiment-files/test_video_4.mp4")

# Run client
# client.run()
