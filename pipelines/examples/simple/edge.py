from edgenet.client import EdgeNetClient
from config import *
from .functions import *

# Initialize client
client = EdgeNetClient(f"ws://{SERVER_HOSTNAME}:{SERVER_PORT}")

# Register functions
# -- Edge-only add three numbers:
client.register_function(EDGE_ONLY_FUNCTION_NAME, edge_add_three_numbers)
# -- Cloud-only emitting of three numbers:
client.register_function(CLOUD_ONLY_FUNCTION_NAME, client.uses_sender(send_three_numbers))

# Run client
client.run()
