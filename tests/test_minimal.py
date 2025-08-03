import os

def test_project_files_exist():
    """测试项目文件是否存在"""
    files = [
        "config.py",
        "video_slicer_ui.py", 
        "pipeline_main.py",
        "predictor.py",
        "utils.py",
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

def test_predictor_constants():
    """测试predictor模块的常量定义"""
    # 直接检查predictor.py文件中的常量定义
    with open("predictor.py", "r", encoding="utf-8") as f:
        content = f.read()
        assert "CLASS_NAMES = [\"loading\", \"map\", \"other\"]" in content
        assert "LABEL_MAP = {\"map\": 0, \"loading\": 1, \"other\": 2}" in content

def test_basic_functionality():
    """测试基本功能"""
    # 测试LABEL_MAP的值（不导入predictor模块）
    expected_label_map = {"map": 0, "loading": 1, "other": 2}
    
    # 直接检查predictor.py文件中的LABEL_MAP定义
    with open("predictor.py", "r", encoding="utf-8") as f:
        content = f.read()
        assert "LABEL_MAP = {\"map\": 0, \"loading\": 1, \"other\": 2}" in content 