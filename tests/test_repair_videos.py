import os
import sys
import pytest
import tempfile

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repair_videos import repair_directory

def test_repair_directory_nonexistent():
    """测试修复不存在的目录"""
    non_existent_dir = "/non/existent/directory"
    
    # 应该正常处理（打印错误信息但不抛出异常）
    repair_directory(non_existent_dir)

def test_repair_directory_empty():
    """测试修复空目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 空目录应该正常处理
        repair_directory(temp_dir)

def test_repair_directory_no_mp4():
    """测试没有MP4文件的目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建一些非MP4文件
        with open(os.path.join(temp_dir, "test.txt"), "w") as f:
            f.write("test")
        
        # 应该正常处理
        repair_directory(temp_dir) 