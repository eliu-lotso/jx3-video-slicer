import os
import subprocess
import shutil
import re
from config import FFMPEG_PATH as CFG_FFMPEG_PATH

if os.path.isfile(CFG_FFMPEG_PATH):
    FFMPEG_PATH = CFG_FFMPEG_PATH
else:
    FFMPEG_PATH = "ffmpeg"

def extract_frames_ffmpeg(video_path, output_dir, fps=2, width=640, progress_callback=None):
    """使用 FFmpeg 抽取视频帧"""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        FFMPEG_PATH, "-y", "-threads", "4",
        "-i", video_path,
        "-vf", f"fps={fps},scale={width}:-1",
        os.path.join(output_dir, "frame_%05d.jpg")
    ]

    print("正在执行命令:", " ".join(cmd), flush=True)
    process = subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        bufsize=1, text=True, encoding="utf-8", errors="ignore"
    )

    frame_count = 0
    buffer = ""
    while True:
        ch = process.stderr.read(1)
        if not ch:
            break
        if ch in ("\r", "\n"):
            if buffer:
                match = re.search(r"frame=\s*(\d+)", buffer)
                if match:
                    frame_count = int(match.group(1))
                    if progress_callback and frame_count % 10 == 0:
                        progress_callback(frame_count)
                clean_line = ''.join(c for c in buffer.strip() if 32 <= ord(c) <= 126)
                if "error" in clean_line.lower() or "fail" in clean_line.lower():
                    print(clean_line, flush=True)
                buffer = ""
        else:
            buffer += ch

    if buffer:
        match = re.search(r"frame=\s*(\d+)", buffer)
        if match:
            frame_count = int(match.group(1))
            if progress_callback:
                progress_callback(frame_count)
        clean_line = ''.join(c for c in buffer.strip() if 32 <= ord(c) <= 126)
        if "error" in clean_line.lower() or "fail" in clean_line.lower():
            print(clean_line, flush=True)

    process.wait()
    return frame_count

def clear_gpu_memory(models_dict):
    """清理显存"""
    import gc
    import torch
    for model in models_dict.values():
        del model
    models_dict.clear()
    torch.cuda.empty_cache()
    gc.collect()
