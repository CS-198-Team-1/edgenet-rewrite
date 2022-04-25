EDGE_FUNCTION_NAME = "edge_stream_video"
EXPERIMENT_VIDEO_PATH = "experiment-files/test_video_4.mp4"
VIDEO_WIDTH  = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS    = 30
CAPTURE_FPS  = 10

BASE_CONFIDENCE = 0.3

MODEL_PATH = "tensorflow/efficientdet_edgetpu.tflite"
RECOG_MODEL_PATH = "tensorflow/depthwise_model_randomchars_perspective_tflite.tflite"
GPX_PATH = "experiment-files/exp_1.gpx"

ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0987654321 "