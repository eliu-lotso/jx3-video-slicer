import os
import sys
import pytest
import tempfile

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slicer import LABEL_MAP, slice_video_by_sequence_incremental

def test_label_map():
    """测试标签映射"""
    assert LABEL_MAP is not None
    assert isinstance(LABEL_MAP, dict)
    assert "map" in LABEL_MAP
    assert "loading" in LABEL_MAP
    assert "other" in LABEL_MAP
    assert LABEL_MAP["map"] == 0
    assert LABEL_MAP["loading"] == 1
    assert LABEL_MAP["other"] == 2

def test_slice_video_empty_labels():
    """测试空标签列表的切片"""
    with tempfile.TemporaryDirectory() as temp_dir:
        fake_video_path = os.path.join(temp_dir, "fake_video.mp4")
        
        # 创建空标签列表
        empty_labels = []
        
        # 应该正常处理（跳过切片）
        slice_video_by_sequence_incremental(
            video_path=fake_video_path,
            labels=empty_labels,
            output_dir=temp_dir,
            fps=2,
            min_segment_sec=5
        )

def test_slice_video_invalid_video_path():
    """测试无效视频路径的切片"""
    with tempfile.TemporaryDirectory() as temp_dir:
        non_existent_video = os.path.join(temp_dir, "non_existent.mp4")
        
        # 创建一些测试标签
        test_labels = ["loading", "map", "loading"]
        
        # 应该抛出异常
        with pytest.raises(Exception):
            slice_video_by_sequence_incremental(
                video_path=non_existent_video,
                labels=test_labels,
                output_dir=temp_dir,
                fps=2,
                min_segment_sec=5
            ) 