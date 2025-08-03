import os
import sys
import pytest

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BASE_DIR, VIDEO_DIR, OUTPUT_DIR, MODEL_DIR, TEMP_FRAME_DIR, FFMPEG_PATH, FFPROBE_PATH

def test_config_paths():
    """测试配置文件中的路径设置"""
    assert BASE_DIR is not None
    assert isinstance(BASE_DIR, str)
    assert os.path.exists(BASE_DIR)
    
    assert VIDEO_DIR is not None
    assert isinstance(VIDEO_DIR, str)
    
    assert OUTPUT_DIR is not None
    assert isinstance(OUTPUT_DIR, str)
    
    assert MODEL_DIR is not None
    assert isinstance(MODEL_DIR, str)
    
    assert TEMP_FRAME_DIR is not None
    assert isinstance(TEMP_FRAME_DIR, str)
    
    assert FFMPEG_PATH is not None
    assert isinstance(FFMPEG_PATH, str)
    
    assert FFPROBE_PATH is not None
    assert isinstance(FFPROBE_PATH, str)

def test_path_consistency():
    """测试路径一致性"""
    assert VIDEO_DIR == os.path.join(BASE_DIR, "videos")
    assert OUTPUT_DIR == os.path.join(BASE_DIR, "slices")
    assert MODEL_DIR == os.path.join(BASE_DIR, "models")
    assert TEMP_FRAME_DIR == os.path.join(BASE_DIR, "temp_frames")
    assert FFMPEG_PATH == os.path.join(BASE_DIR, "bin", "ffmpeg.exe")
    assert FFPROBE_PATH == os.path.join(BASE_DIR, "bin", "ffprobe.exe") 