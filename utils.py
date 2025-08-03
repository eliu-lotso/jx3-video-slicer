import os
import subprocess
import shutil
import re
from config import FFMPEG_PATH as CFG_FFMPEG_PATH

if os.path.isfile(CFG_FFMPEG_PATH):
    FFMPEG_PATH = CFG_FFMPEG_PATH
else:
    FFMPEG_PATH = "ffmpeg"

def repair_directory(video_dir):
    """标准化处理指定目录下的所有 MP4 视频文件"""
    if not os.path.isdir(video_dir):
        print(f"目录不存在: {video_dir}")
        return

    videos = [f for f in os.listdir(video_dir) if f.lower().endswith(".mp4")]
    videos.sort()
    repaired_count = 0

    for filename in videos:
        video_path = os.path.join(video_dir, filename)
        print(f"标准化处理视频: {filename}")
        temp_path = os.path.join(video_dir, "temp.mp4")

        if os.path.exists(temp_path):
            os.remove(temp_path)

        try:
            result = subprocess.run(
                [FFMPEG_PATH, "-y", "-i", video_path, "-c", "copy", "-movflags", "+faststart", temp_path],
                capture_output=True, text=True, encoding="utf-8"
            )
        except FileNotFoundError:
            print("❌ 未找到 FFmpeg 可执行文件，请确认路径设置正确。")
            return

        if result.returncode != 0:
            print(f"⚠️ FFmpeg 处理失败: {filename}\\n{result.stderr}")
        else:
            try:
                os.replace(temp_path, video_path)
                repaired_count += 1
                print(f"✅ 修复完成: {filename}")
            except Exception as e:
                print(f"❌ 替换失败: {filename} -> {e}")

    print(f"🧹 标准化处理完成，共处理 {repaired_count} 个视频。")

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
