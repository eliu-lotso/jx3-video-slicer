import os
import sys
import pytest

def test_project_structure():
    """测试项目基本结构"""
    # 检查必要的文件是否存在
    required_files = [
        "config.py",
        "video_slicer_ui.py",
        "pipeline_main.py",
        "pipeline_worker.py",
        "predictor.py",
        "slicer.py",
        "utils.py",
        "repair_videos.py",
        "requirements.txt",
        "README.md",
        "LICENSE"
    ]
    
    for file_name in required_files:
        assert os.path.exists(file_name), f"Required file {file_name} not found"

def test_config_import():
    """测试配置模块导入"""
    try:
        import config
        assert hasattr(config, 'BASE_DIR')
        assert hasattr(config, 'VIDEO_DIR')
        assert hasattr(config, 'OUTPUT_DIR')
        assert hasattr(config, 'MODEL_DIR')
        assert hasattr(config, 'TEMP_FRAME_DIR')
        assert hasattr(config, 'FFMPEG_PATH')
        assert hasattr(config, 'FFPROBE_PATH')
    except ImportError as e:
        pytest.fail(f"Failed to import config module: {e}")

def test_predictor_import():
    """测试预测模块导入"""
    try:
        import predictor
        assert hasattr(predictor, 'CLASS_NAMES')
        assert hasattr(predictor, 'load_model_timm')
        assert hasattr(predictor, 'predict_labels')
        assert isinstance(predictor.CLASS_NAMES, list)
        assert len(predictor.CLASS_NAMES) == 3
    except ImportError as e:
        pytest.fail(f"Failed to import predictor module: {e}")

def test_slicer_import():
    """测试切片模块导入"""
    try:
        import slicer
        assert hasattr(slicer, 'LABEL_MAP')
        assert hasattr(slicer, 'slice_video_by_sequence_incremental')
        assert isinstance(slicer.LABEL_MAP, dict)
    except ImportError as e:
        pytest.fail(f"Failed to import slicer module: {e}")

def test_utils_import():
    """测试工具模块导入"""
    try:
        import utils
        assert hasattr(utils, 'extract_frames_ffmpeg')
        assert hasattr(utils, 'clear_gpu_memory')
    except ImportError as e:
        pytest.fail(f"Failed to import utils module: {e}")

def test_repair_videos_import():
    """测试视频修复模块导入"""
    try:
        import repair_videos
        assert hasattr(repair_videos, 'repair_directory')
    except ImportError as e:
        pytest.fail(f"Failed to import repair_videos module: {e}")

def test_pipeline_import():
    """测试管道模块导入"""
    try:
        import pipeline_main
        import pipeline_worker
        assert hasattr(pipeline_main, 'run_pipeline')
        assert hasattr(pipeline_worker, 'process_single_video')
    except ImportError as e:
        pytest.fail(f"Failed to import pipeline modules: {e}")

def test_class_names():
    """测试类别名称"""
    import predictor
    expected_classes = ["loading", "map", "other"]
    assert predictor.CLASS_NAMES == expected_classes

def test_label_map():
    """测试标签映射"""
    import slicer
    expected_mapping = {"map": 0, "loading": 1, "other": 2}
    assert slicer.LABEL_MAP == expected_mapping 