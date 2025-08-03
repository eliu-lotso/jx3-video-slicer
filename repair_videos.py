import os
import subprocess
from config import FFMPEG_PATH

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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="强制标准化所有 MP4 视频")
    parser.add_argument("--video_dir", required=True)
    args = parser.parse_args()
    repair_directory(args.video_dir)
