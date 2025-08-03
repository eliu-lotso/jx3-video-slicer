import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

VIDEO_DIR = os.path.join(BASE_DIR, "videos")
OUTPUT_DIR = os.path.join(BASE_DIR, "slices")
MODEL_DIR = os.path.join(BASE_DIR, "models")
TEMP_FRAME_DIR = os.path.join(BASE_DIR, "temp_frames")

FFMPEG_PATH = os.path.join(BASE_DIR, "bin", "ffmpeg.exe")
FFPROBE_PATH = os.path.join(BASE_DIR, "bin", "ffprobe.exe")
