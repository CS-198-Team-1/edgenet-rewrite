import csv, json, glob, os
from dateutil import parser as dttm_parser
from argparse import ArgumentParser as ArgParser

all_results = glob.glob("./*.results.csv")

# Build statistics dictionary
statistics = {}
for _fname in all_results:
    if "rpi" not in _fname: continue

    # Get experiment information from filename:
    fname = os.path.basename(_fname)[:-12]
    pipeline, capture_rate, edge_n, bw_constraint, session_id, iteration = fname.split("_")
    capture_rate = f"{capture_rate} CPS"
    edge_n = f"{edge_n} edge{'s' if int(edge_n) > 1 else ''}"
    
    with open(_fname) as _file:
        reader = csv.reader(_file, delimiter=",")

        # Calculate capture-to-result latency:
        ctr_seconds = None
        for row in reader:
            raw_result = row[1].replace("'", '"')
            result = json.loads(raw_result)

            if not result["time_captured"]: continue
            
            captured_time = dttm_parser.parse(result["time_captured"]).replace(tzinfo=None)
            try:
                result_time = dttm_parser.parse(result["time_now"]).replace(tzinfo=None)
            except KeyError as e:
                result_time = dttm_parser.parse(result["time_recognized"]).replace(tzinfo=None)

            ctr_seconds = (result_time - captured_time).total_seconds()

            if ctr_seconds < 0:
                if pipeline == "hybrid":
                    ctr_seconds = (result_time - captured_time).total_seconds() + 28800
                # else:
                #     raise Exception(f"{_fname},{ctr_seconds}, {result_time}, {captured_time}")
                ctr_seconds = max(0, ctr_seconds)

            # Add count and acc. sum per hierarchy:
            hierarchy = ["pipeline", "capture_rate", "edge_n", "bw_constraint"]
            current = statistics
            for pos in hierarchy:
                # If unpopulated:
                position_name = locals()[pos]
                if position_name not in current:
                    current[ position_name ] = {
                        "sum": ctr_seconds,
                        "max": ctr_seconds,
                        "min": ctr_seconds,
                        "count": 1,
                    } 
                else:
                    current[ position_name ]["sum"]   += ctr_seconds
                    current[ position_name ]["count"] += 1
                    current[ position_name ]["max"]   = max(ctr_seconds, current[ position_name ]["max"])
                    current[ position_name ]["min"]   = min(ctr_seconds, current[ position_name ]["min"])
                # Step up hierarchy
                current = current[ position_name ]

# Get averages
def get_avg(_dict):
    _dict["average"] = _dict["sum"] / float(_dict["count"])

def traverse_stat(level):
    for key, value in level.items():
        if type(value) is dict:
            get_avg(value)
            traverse_stat(value)


traverse_stat(statistics)
# current = statistics
# for key in current:
#     value = current[key]
#     if type(pos) 

# hierarchy = ["pipeline", "capture_rate", "edge_n", "bw_constraint"]
# current = statistics
# for pos in hierarchy:
#     # If unpopulated:
#     position_name = locals()[pos]
#     curr_pos = current[position_name]
#     curr_pos["average"] = curr_pos["sum"] / float(curr_pos["count"])
#     # Step up hierarchy
#     current = current[ position_name ]

print(json.dumps(statistics, indent=2, sort_keys=True))



# # Consolidate averaged_out data
# for pipeline in FILES:
#     CTRS[pipeline] = {}
#     for edge_n in FILES[pipeline]:
#         CTRS[pipeline][edge_n] = {"sum": 0, "average": None, "count": 0}
#         for file in FILES[pipeline][edge_n]:
#             with open(file) as fp:
#                 reader = csv.reader(fp, delimiter=",")
#                 for row in reader:
#                     raw_result = row[1].replace("'", '"')
#                     result = json.loads(raw_result)

#                     if not result["time_captured"]: continue
                    
#                     captured_time = dttm_parser.parse(result["time_captured"]).replace(tzinfo=None)
#                     try:
#                         result_time = dttm_parser.parse(result["time_now"]).replace(tzinfo=None)
#                     except KeyError as e:
#                         result_time = dttm_parser.parse(result["time_recognized"]).replace(tzinfo=None)

#                     ctr_seconds = (result_time - captured_time).total_seconds()
                    
#                     CTRS[pipeline][edge_n]["sum"]   += ctr_seconds
#                     CTRS[pipeline][edge_n]["count"] += 1

#         CTRS[pipeline][edge_n]["average"] = CTRS[pipeline][edge_n]["sum"] / float(CTRS[pipeline][edge_n]["count"])

# print(json.dumps(CTRS, indent=2, sort_keys=True))

