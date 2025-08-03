import os
import pytest

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

def test_directories_exist():
    """测试目录是否存在"""
    directories = [
        "bin",
        "models",
        "tests"
    ]
    
    for directory in directories:
        assert os.path.exists(directory), f"Directory {directory} does not exist"

def test_basic_imports():
    """测试基本导入"""
    # 测试config模块
    try:
        import config
        assert True
    except ImportError:
        pytest.fail("Cannot import config module")

def test_class_names():
    """测试类别名称"""
    try:
        import predictor
        assert predictor.CLASS_NAMES == ["loading", "map", "other"]
    except ImportError:
        pytest.fail("Cannot import predictor module")

def test_label_mapping():
    """测试标签映射"""
    try:
        import slicer
        expected = {"map": 0, "loading": 1, "other": 2}
        assert slicer.LABEL_MAP == expected
    except ImportError:
        pytest.fail("Cannot import slicer module")

def test_requirements_file():
    """测试requirements.txt文件"""
    with open("requirements.txt", "r") as f:
        content = f.read()
        assert "torch" in content
        assert "opencv-python" in content
        assert "PyQt5" in content
        assert "pytest" in content 