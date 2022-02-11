import time
from config import *


EDGE_ONLY_FUNCTION_NAME = "edge_add_three_numbers"
CLOUD_ONLY_FUNCTION_NAME = "cloud_add_three_numbers"

def add_three_numbers(a, b, c):
    logging.info(f"Function call received for a={a}, b={b}, c={c}")
    return a + (2*b) + (3*c)

def send_three_numbers(sender, times):
    logging.info(f"Preparing to send out three numbers to server...")
    for i in range(times):
        time.sleep(0.1)
        a, b, c = i, i+6, i+10
        sender.send_result({
            "args": (a, b, c),
            "kwargs": {}
        })
        logging.info(f"Numbers {(a, b, c)} sent to server. Expect a result of {add_three_numbers(a, b, c)}" )

edge_add_three_numbers = add_three_numbers
cloud_add_three_numbers = add_three_numbers
