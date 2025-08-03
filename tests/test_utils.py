import os
import sys
import pytest
import tempfile
import shutil

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import extract_frames_ffmpeg, clear_gpu_memory

def test_clear_gpu_memory():
    """测试GPU内存清理函数"""
    # 创建一个空的模型字典
    models_dict = {}
    
    # 测试函数不会抛出异常
    try:
        clear_gpu_memory(models_dict)
        assert True  # 如果执行到这里说明没有异常
    except Exception as e:
        pytest.fail(f"clear_gpu_memory raised an exception: {e}")

def test_extract_frames_ffmpeg_missing_video():
    """测试处理不存在的视频文件"""
    with tempfile.TemporaryDirectory() as temp_dir:
        non_existent_video = os.path.join(temp_dir, "non_existent.mp4")
        output_dir = os.path.join(temp_dir, "frames")
        
        # 应该抛出异常或返回错误
        with pytest.raises(Exception):
            extract_frames_ffmpeg(non_existent_video, output_dir)

def test_extract_frames_ffmpeg_invalid_params():
    """测试无效参数"""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, "frames")
        
        # 测试空路径
        with pytest.raises(Exception):
            extract_frames_ffmpeg("", output_dir)
        
        # 测试None路径
        with pytest.raises(Exception):
            extract_frames_ffmpeg(None, output_dir) 