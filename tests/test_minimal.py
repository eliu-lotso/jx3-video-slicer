import os

def test_project_files_exist():
    """测试项目文件是否存在"""
    files = [
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
    
    for file in files:
        assert os.path.exists(file), f"File {file} does not exist"

def test_tests_directory_exists():
    """测试tests目录是否存在"""
    assert os.path.exists("tests"), "tests directory does not exist"

def test_config_import():
    """测试config模块导入"""
    import config
    assert hasattr(config, 'BASE_DIR')
    assert hasattr(config, 'VIDEO_DIR')
    assert hasattr(config, 'OUTPUT_DIR')
    assert hasattr(config, 'MODEL_DIR')
    assert hasattr(config, 'TEMP_FRAME_DIR')
    assert hasattr(config, 'FFMPEG_PATH')
    assert hasattr(config, 'FFPROBE_PATH')

def test_predictor_import():
    """测试predictor模块导入"""
    import predictor
    assert hasattr(predictor, 'CLASS_NAMES')
    assert predictor.CLASS_NAMES == ["loading", "map", "other"]

def test_slicer_import():
    """测试slicer模块导入"""
    import slicer
    assert hasattr(slicer, 'LABEL_MAP')
    expected = {"map": 0, "loading": 1, "other": 2}
    assert slicer.LABEL_MAP == expected 