import subprocess
import shutil
import sys
import os
from config import BASE_DIR
import repair_videos

def run_pipeline(video_dir, output_dir, logger=print, cancel_flag=lambda: False, process_list=None):

    logger("启动视频标准化处理...")
    repair_videos.repair_directory(video_dir)

    videos = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]
    videos.sort()

    if cancel_flag():
        logger("任务已取消，跳过视频处理。")
        return

    logger("开始串行处理视频（子进程方式）...")
    logger(f"共检测到 {len(videos)} 个视频文件")

    exe_path = os.path.join(BASE_DIR, "pipeline_worker.exe")
    use_exe = os.path.isfile(exe_path)
    if not use_exe:
        logger("⚠️ 未找到 pipeline_worker.exe，将回退调用 .py 脚本（仅测试环境）")

    try:
        for i, v in enumerate(videos):
            if cancel_flag():
                logger("任务已取消，中止处理。")
                return

            video_path  = os.path.join(video_dir, v)
            output_path = os.path.join(output_dir, os.path.splitext(v)[0])
            os.makedirs(output_path, exist_ok=True)

            if use_exe:
                cmd = [
                    exe_path,
                    "--video_path",  video_path,
                    "--output_path", output_path,
                    "--index",       str(i),
                    "--total",       str(len(videos)),
                ]
            else:
                script_path = os.path.join(BASE_DIR, "pipeline_worker.py")
                cmd = [
                    sys.executable,
                    script_path,
                    "--video_path",  video_path,
                    "--output_path", output_path,
                    "--index",       str(i),
                    "--total",       str(len(videos)),
                ]

            logger(f"启动子进程处理视频: {v}  (use_exe={use_exe})")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            if process_list is not None:
                process_list.append(process)

            try:
                for line in process.stdout:
                    if cancel_flag():
                        logger("检测到取消信号，终止子进程...")
                        process.terminate()
                        break
                    line = line.strip()
                    if line:
                        logger(line)
            except Exception:
                pass

            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger("子进程响应超时，强制杀死...")
                process.kill()

            if process.returncode != 0:
                logger(f"⚠️ 视频处理失败: {v}，退出码: {process.returncode}")
                return

        logger("✅ 所有视频处理完成")

    finally:
        if os.path.isdir(output_dir):
            for sub in os.listdir(output_dir):
                temp_dir = os.path.join(output_dir, sub, "temp_frames")
                if os.path.isdir(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="视频流水线主程序")
    parser.add_argument("--video_dir",  required=True, help="视频文件夹路径")
    parser.add_argument("--output_dir", required=True, help="输出切片目录")
    args = parser.parse_args()
    run_pipeline(args.video_dir, args.output_dir)
