EDGE_ONLY_FUNCTION_NAME = "edge_add_three_numbers"
CLOUD_ONLY_FUNCTION_NAME = "cloud_add_three_numbers"

def add_three_numbers(a, b, c):
    return a + (2*b) + (3*c)

def send_three_numbers(send_result):
    for i in range(30):
        send_result({
            "args": (i, i+6, i+10),
            "kwargs": {}
        })

edge_add_three_numbers = add_three_numbers
cloud_add_three_numbers = add_three_numbers
