#!/usr/bin/env python3
"""
剑网三视频切片工具发布脚本
用于准备GitHub发布包
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_release_package():
    """创建发布包"""
    release_dir = "release"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # 复制核心文件
    core_files = [
        "video_slicer_ui.py",
        "pipeline_main.py", 
        "pipeline_worker.py",
        "predictor.py",
        "slicer.py",
        "utils.py",
        "repair_videos.py",
        "config.py",
        "requirements.txt",
        "README.md",
        "LICENSE"
    ]
    
    for file in core_files:
        if os.path.exists(file):
            shutil.copy2(file, release_dir)
    
    # 复制目录
    dirs_to_copy = ["bin", "models"]
    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(release_dir, dir_name))
    
    # 创建zip包
    zip_name = "jx3-video-slicer-v1.0.0.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, release_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ 发布包已创建: {zip_name}")
    print(f"📁 发布目录: {release_dir}")
    
    # 清理临时目录
    shutil.rmtree(release_dir)

if __name__ == "__main__":
    create_release_package() 