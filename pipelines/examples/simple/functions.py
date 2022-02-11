import time
from config import *
from metrics.time import uses_timer


EDGE_ONLY_FUNCTION_NAME = "edge_add_three_numbers"
CLOUD_ONLY_FUNCTION_NAME = "cloud_add_three_numbers"

def add_three_numbers(a, b, c):
    time.sleep(0.1)
    logging.info(f"Function call received for a={a}, b={b}, c={c}")
    return a + (2*b) + (3*c)

@uses_timer
def send_three_numbers(timer, sender, times):
    logging.info(f"Preparing to send out three numbers to server...")
    timer.start_section("initial-sleep")
    time.sleep(0.2)
    timer.end_section("initial-sleep")
    for i in range(times):
        timer.start_looped_section("looper")
        time.sleep(0.1)
        a, b, c = i, i+6, i+10
        sender.send_result({
            "args": (a, b, c),
            "kwargs": {}
        })
        timer.end_looped_section("looper")
        logging.info(f"Numbers {(a, b, c)} sent to server. Expect a result of {add_three_numbers(a, b, c)}" )
    timer.end_function()
    sender.send_metrics(timer)


edge_add_three_numbers = add_three_numbers
cloud_add_three_numbers = add_three_numbers
