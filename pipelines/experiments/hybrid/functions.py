import codecs, pickle, re, datetime, cv2, numpy as np, tensorflow as tf
from gpx import uses_gpx
from metrics.time import uses_timer
from .constants import *
from config import *

CHARS = "ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789" # exclude I, O
CHARS_DICT = {char:i for i, char in enumerate(CHARS)}
DECODE_DICT = {i:char for i, char in enumerate(CHARS)}

#Initialize recognition model
recog_interpreter = tf.lite.Interpreter(model_path=RECOG_MODEL_PATH)
recog_interpreter.allocate_tensors()
recog_input_details = recog_interpreter.get_input_details()
recog_output_details = recog_interpreter.get_output_details()

# License plate pattern for PH plates
lph_pattern = re.compile("^[A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9]?$")

# We will relegate adding the uses_sender decorator in client.py
@uses_timer
@uses_gpx(GPX_PATH)
def capture_video(gpxc, timer, sender, video_path, frames_per_second=CAPTURE_FPS, target="all"):
    # OpenCV initialization
    timer.start_section("edge-initialization")

    cap = cv2.VideoCapture(video_path)
    interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    frame_counter = 0 # Frame counter
    every_n_frames = int(frames_per_second) / float(VIDEO_FPS) # Check every n frames
    capture_acc = 0
    start_time = datetime.datetime.now()

    print(start_time.isoformat(), gpxc.start_time.isoformat())

    timer.end_section("edge-initialization")

    while cap.isOpened():

        frame_counter += 1

        # if frame_counter % VIDEO_FPS == 0:
        required_delta = datetime.timedelta(
            seconds=frame_counter / VIDEO_FPS
        ) # Make sure we don't "look into the future"

        while (datetime.datetime.now() - start_time) < required_delta:
            pass # Loop while sufficient time has not yet passed

        timer.start_looped_section("edge-frame-capture")
        ret, frame = cap.read() # Capture each frame of video
        timer.end_looped_section("edge-frame-capture")

        capture_acc += every_n_frames
        if capture_acc < 1.0:
            continue
        else:
            capture_acc -= 1.0    

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
        ctr = 0
        for i, confidence in enumerate(output_data[0]):
            if confidence > BASE_CONFIDENCE and ctr == 0:
                ctr +=1
                timer.start_looped_section("edge-plate-transmission")
                _box = boxes[0][i]
                x1, x2, y1, y2 = _box[1], _box[3], _box[0], _box[2]
                save_frame = frame[
                    max( 0, int(y1*1079) ) : min( 1079, int(y2*1079) ),
                    max( 0, int(x1*1920) ) : min( 1920, int(x2*1920) )
                ]

                # Save the image
                test_image = cv2.resize(save_frame,(94,24))/256
                test_image = np.expand_dims(test_image,axis=0)
                test_image = test_image.astype(np.float32)

              
                # Encode image
                pickled_image = codecs.encode(pickle.dumps(test_image), "base64").decode()

                # Send the image
                # execute_text_recognition_tflite(
                #     sender, gpxc, 
                #     test_image, confidence,
                #     frame_counter
                # )
                sender.send_result({
                    "cropped_frame": pickled_image,
                    "confidence": int( confidence * 100 ),
                    "frame_counter": frame_counter,
                    "start_time": gpxc.start_time.isoformat()
                })
                timer.end_looped_section("edge-plate-transmission")

    logging.info("End of video detected. Ending execution...")
    # Release capturing
    cap.release()
    logging.info("OpenCV capture released.")

    timer.end_function() # Record end of whole function
    sender.send_metrics(timer) # Send metrics to cloud

def execute_text_recognition_tflite(gpxc, cropped_frame, confidence, frame_counter):
    RECOGNITION_FAILED = (False, 0, 0, 0, 0, 0, 0)

    # Unpack frame
    c_frame = cropped_frame
    cropped_frame = pickle.loads(codecs.decode(cropped_frame.encode(), "base64"))

    # Execute text recognition
    recog_interpreter.set_tensor(recog_input_details[0]['index'], cropped_frame)
    recog_interpreter.invoke()
    output_data = recog_interpreter.get_tensor(recog_output_details[0]['index'])
    decoded = tf.keras.backend.ctc_decode(output_data,(24,),greedy=False)
    text = ""
    for i in np.array(decoded[0][0][0]):
        if i >-1:
            text += DECODE_DICT[i]

    # Do nothing if text is empty
    if not len(text): return RECOGNITION_FAILED
    license_plate = text
    text[:3].replace("0",'O')

    # Do nothing if not a valid plate number
    if not lph_pattern.match(license_plate): return RECOGNITION_FAILED

    # A matching license plate is now found!

    # Get current time
    time_now = datetime.datetime.now().replace(tzinfo=None)

    # Get time plate was captured
    seconds_elapsed = frame_counter / VIDEO_FPS
    time_captured = gpxc.start_time + datetime.timedelta(seconds=seconds_elapsed)

    # Get GPX entry
    gpx_entry = gpxc.get_latest_entry(time_captured)
    lat, lng = gpx_entry.latlng

    print(f"\n\nI:{time_captured.isoformat()} ({gpxc.start_time.isoformat()} + {frame_counter}/{VIDEO_FPS})")
    print(f"R:{time_now.isoformat()}\n\n")

    return (
        True, license_plate, lat, lng, confidence, 
        time_captured.isoformat(), 
        time_now.isoformat()
    )

    # Send result to cloud
    # sender.send_result({
    #     "time_recognized": time_now.isoformat(),
    #     "time_captured": time_captured.isoformat(),
    #     "plate": license_plate,
    #     "confidence": confidence_in_100,
    #     "lat": lat,
    #     "lng": lng,
    # })

class LPRException(Exception): pass
