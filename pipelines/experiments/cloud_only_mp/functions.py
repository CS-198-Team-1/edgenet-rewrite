import re, datetime, cv2, numpy as np, tensorflow as tf, subprocess
import sys, socket, time
from edgenet.job import EdgeNetJobResult
from gpx import uses_gpx
from metrics.time import uses_timer, Timer
from .constants import *
from config import *
import multiprocessing as mp



interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

recog_interpreter = tf.lite.Interpreter(model_path=RECOG_MODEL_PATH)
recog_interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

recog_input_details = recog_interpreter.get_input_details()
recog_output_details = recog_interpreter.get_output_details()


CHARS = "ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789" # exclude I, O
CHARS_DICT = {char:i for i, char in enumerate(CHARS)}
DECODE_DICT = {i:char for i, char in enumerate(CHARS)}

# License plate pattern for PH plates
lph_pattern = re.compile("^[A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9]?$")


@uses_timer
def start_streaming(timer, sender, video_path, stream_to_url):
    time.sleep(2.05)
    args = [
        "ffmpeg", "-re", "-i", video_path, 
        "-c", "copy", "-f", "rtsp", 
        "-rtsp_transport", "tcp", stream_to_url,
    ]

    timer.start_section("edge-stream")
    subprocess.call(args)
    timer.end_section("edge-stream")

    timer.end_function()
    sender.send_metrics(timer)

@uses_timer
@uses_gpx(GPX_PATH)
def capture_video(gpxc, timer, stream_url,  frame_buffer,results,frames_per_second=CAPTURE_FPS, target="all"):
    # OpenCV initialization
    timer.start_section("cloud-initialization")

    while True:
        cap = cv2.VideoCapture(stream_url)
        try:   
            # Check if camera opened successfully
            if (cap.isOpened()== True): 
                print("[INFO] FOUND! Stream Link...")
                break
            # Else is important to display error message on the screen if can.isOpened returns false
            else:
                print("[NO STREAM1]")
        except socket.error:
            print("[NO STREAM2]")
        except:
            print("[FAILED]")
        time.sleep(0.001)

    frame_counter = 0 # Frame counter
    every_n_frames = frames_per_second/float(VIDEO_FPS) # Check every n frames
    capture_acc = 0
    start_time = gpxc.start_time

    print(start_time.isoformat(), gpxc.start_time.isoformat())

    timer.end_section("cloud-initialization")

    while cap.isOpened():
        frame_counter += 1

        if frame_counter % VIDEO_FPS == 0:
            required_delta = datetime.timedelta(
                seconds=frame_counter // VIDEO_FPS
            ) # Make sure we don't "look into the future"
            while (datetime.datetime.now() - start_time) < required_delta:
                time.sleep(0.001)
                pass # Loop while sufficient time has not yet passed

        timer.start_looped_section("cloud-opencv-read")
        ret, frame = cap.read() # Capture each frame of video
        timer.end_looped_section("cloud-opencv-read")

        capture_acc += every_n_frames
        if capture_acc < 1.0:
            continue
        else:
            capture_acc -= 1.0        

        #if frame_counter % every_n_frames != 0:
        #    continue # Only start execution every n frames

        if not ret or frame is None:
            # raise LPRException("cap.read() returned invalid values!")
            break # Execution is finished
            seconds_elapsed = frame_counter / float(VIDEO_FPS)
            delta = datetime.timedelta(seconds=seconds_elapsed)
            time_captured = start_time + delta
        frame_buffer.put((frame,time_captured))

    logging.info("End of video detected. Ending execution...")
    # Release capturing
    cap.release()
    logging.info("OpenCV capture released.")

    timer.end_function() # Record end of whole function

    # # Pickle results
    # timer.pickle("legacy-cloud-only.pickle")
    return timer, results_list


def execute_detection(boxes_queue,frame_queue,frame_buffer, timer):
    print('starting detection')
    
    while True:
        if frame_buffer.empty():
            continue
        timer.start_section("licence_plate_detection")
        frame, time_captured = frame_buffer.get()
        resized = cv2.resize(frame, (320,320), interpolation=cv2.INTER_AREA)

        input_data = resized.astype(np.float32)          # Set as 3D RGB float array
        input_data /= 255.                               # Normalize
        input_data = np.expand_dims(input_data, axis=0)  # Batch dimension (wrap in 4D)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        # Confidence values
        # output_data = [ n = # of classes [ confidence values of boxes ] ]

        # details = [
        #     {"index": [ n = # of classes [ confidence values of boxes ] ]},
        #     {"index": [ n = # of classes [ details of boxes ] ]}
        # ]
        output_data = interpreter.get_tensor(output_details[0]['index'])

        # Bounding boxes
        boxes = interpreter.get_tensor(output_details[1]['index'])
        timer.end_section("licence_plate_detection")
        for i, confidence in enumerate(output_data[0]):
            if confidence > .3:
                frame_queue.put(frame,time_captured)
                boxes_queue.put(boxes[0][i])

def execute_text_recognition( boxes_queue, frame_queue, results, gpxc, timer):
    while True:
        if frame_queue.empty():
            continue
        timer.start_section("licence_plate_recognition")
        boxes = boxes_queue.get()
        frame,time_captured = frame_queue.get()
        x1, x2, y1, y2 = boxes[1], boxes[3], boxes[0], boxes[2]
        save_frame = frame[
            max( 0, int(y1*1079) ) : min( 1079, int(y2*1079) ),
            max( 0, int(x1*1920) ) : min( 1920, int(x2*1920) )
        ]

        test_image = cv2.resize(save_frame,(94,24))/256
        test_image = np.expand_dims(test_image,axis=0)
        test_image = test_image.astype(np.float32)
        interpreter.set_tensor(input_details[0]['index'], test_image)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        decoded = tf.keras.backend.ctc_decode(output_data,(24,),greedy=False)
        text = ""
        for i in np.array(decoded[0][0][0]):
            if i >-1:
                text += DECODE_DICT[i]
        # Do nothing if text is empty
        if not len(text): return 
        license_plate = text
        text[:3].replace("0",'O')

        # Do nothing if not a valid plate number
        if not lph_pattern.match(license_plate): return 

        # A matching license plate is now found!
        time_now = datetime.datetime.now().replace(tzinfo=None)
        gpx_entry = gpxc.get_latest_entry(time_captured)
        lat, lng = gpx_entry.latlng

        logging.info(f"License plate found! {license_plate} ({lat}, {lng})")

        # Record result
        result = {
            "time_now": time_now.isoformat(),
            "time_captured": time_captured.isoformat(),
            "plate": license_plate,
            "lat": lat,
            "lng": lng,
        }

        job_result = EdgeNetJobResult("cloud", result, None, None)
        timer.end_section("licence_plate_recognition")
        results.put(job_result)

@uses_timer
@uses_gpx(GPX_PATH)
def cloud_engine(gpxc, timer, stream_url, frames_per_second=CAPTURE_FPS, target="all", results_list=[]):
    processes = []
    frame_buffer = mp.Queue()
    frame_queue = mp.Queue()
    boxes_queue = mp.Queue()
    results = mp.Queue()

    # Start streaming
    p = mp.Process(target=capture_video,
                    args=(gpxc, timer, stream_url, frame_buffer,results),
                    daemon=True)
    p.start()
    processes.append(p)

    # Activation of detection model
    p = mp.Process(target=execute_detection,
                    args=(boxes_queue,frame_queue,frame_buffer, timer),
                    daemon=True)
    p.start()
    processes.append(p)

    # Activation of recognition model
    p = mp.Process(target=execute_text_recognition,
                    args=(boxes_queue,frame_queue, results, gpxc,timer),
                    daemon=True)
    p.start()
    processes.append(p)

    for p in processes:
        p.join()
    return timer, list(results)


class LPRException(Exception): pass


if __name__ == "__main__":
    capture_video(sys.argv[1])