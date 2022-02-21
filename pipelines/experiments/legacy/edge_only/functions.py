import re, datetime, cv2, easyocr, numpy as np, tensorflow as tf
from gpx import uses_gpx
from metrics.time import uses_timer
from .constants import *
from config import *


# License plate pattern for PH plates
lph_pattern = re.compile("^[A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9]?$")


# We will relegate adding the uses_sender decorator in client.py
@uses_timer
@uses_gpx(GPX_PATH)
def capture_video(gpxc, timer, sender, video_path, frames_per_second=15, target="all"):
    # OpenCV initialization
    timer.start_section("edge-initialization")

    cap = cv2.VideoCapture(video_path)
    interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    frame_counter = 0 # Frame counter
    every_n_frames = VIDEO_FPS // frames_per_second # Check every n frames
    start_time = datetime.datetime.now()

    print(start_time.isoformat(), gpxc.start_time.isoformat())

    timer.end_section("edge-initialization")

    while cap.isOpened():

        frame_counter += 1

        if frame_counter % VIDEO_FPS == 0:
            required_delta = datetime.timedelta(
                seconds=frame_counter // VIDEO_FPS
            ) # Make sure we don't "look into the future"

            while (datetime.datetime.now() - start_time) < required_delta:
                pass # Loop while sufficient time has not yet passed

        if frame_counter % every_n_frames != 0:
            continue # Only start execution every n frames

        ret, frame = cap.read() # Capture each frame of video

        if not ret or frame is None:
            # raise LPRException("cap.read() returned invalid values!")
            break # Execution is finished

        logging.info("[{:06d}][{}fps] Processing frames...".format(frame_counter, frames_per_second))

        timer.start_looped_section("edge-plate-detection")

        # Execute detection:
        # -- Resize frame to 320x320 square
        resized = cv2.resize(frame, (320,320), interpolation=cv2.INTER_AREA)
        input_data = resized.astype(np.float32)          # Set as 3D RGB float array
        input_data /= 255.                               # Normalize
        input_data = np.expand_dims(input_data, axis=0)  # Batch dimension (wrap in 4D)

        # Initialize input tensor
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

        timer.end_looped_section("edge-plate-detection")

        # For index and confidence value of the first class [0]
        for i, confidence in enumerate(output_data[0]):
            if confidence > BASE_CONFIDENCE:
<<<<<<< HEAD:pipelines/experiments/edge_only/functions.py
                execute_text_recognition_tflite(
                    send_result, gpxc, 
                    boxes[0][i], frame, confidence,
                    recog_interpreter,recog_input_details,recog_output_details
=======
                timer.start_looped_section("edge-plate-recognition")

                # Get exact time captured based on frame # and FPS
                seconds_elapsed = frame_counter / float(VIDEO_FPS)
                delta = datetime.timedelta(seconds=seconds_elapsed)
                time_captured = start_time + delta

                execute_text_recognition(
                    sender, gpxc, 
                    boxes[0][i], frame, confidence, time_captured
>>>>>>> origin/master:pipelines/experiments/legacy/edge_only/functions.py
                )
                timer.end_looped_section("edge-plate-recognition")

    logging.info("End of video detected. Ending execution...")
    # Release capturing
    cap.release()
    logging.info("OpenCV capture released.")

    timer.end_function() # Record end of whole function
    sender.send_metrics(timer) # Send metrics to cloud


def execute_text_recognition(sender, gpxc, boxes, frame, confidence, time_captured):
    x1, x2, y1, y2 = boxes[1], boxes[3], boxes[0], boxes[2]
    save_frame = frame[
        max( 0, int(y1*1079) ) : min( 1079, int(y2*1079) ),
        max( 0, int(x1*1920) ) : min( 1079, int(x2*1920) )
    ]
    confidence_in_100 = int( confidence * 100 )

    # Execute text recognition
    reader = easyocr.Reader(["en"])
    text = reader.readtext(save_frame, allowlist=ALLOWED_CHARS)

    # Do nothing if text is empty
    if not len(text): return 

    # Preprocess plate text
    license_plate = text[0][1].upper()
    license_plate = license_plate.replace(" ", "")

    # Check if license plate matches pattern
    license_plate = text[0][1].upper()
    license_plate = license_plate.replace(" ", "")

    # Do nothing if not a valid plate number
    if not lph_pattern.match(license_plate): return 

    # A matching license plate is now found!
    time_now = datetime.datetime.now().replace(tzinfo=None)
    gpx_entry = gpxc.get_latest_entry(time_captured)
    lat, lng = gpx_entry.latlng
    
    logging.info(f"License plate found! {license_plate} ({lat}, {lng})")

    # Send result to cloud
    sender.send_result({
        "time_now": time_now.isoformat(),
        "time_captured": time_captured.isoformat(),
        "plate": license_plate,
        "lat": lat,
        "lng": lng,
    })


class LPRException(Exception): pass
