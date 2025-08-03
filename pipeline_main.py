import subprocess
import shutil
import sys
import os
import cv2
import math
import argparse
from config import BASE_DIR
from utils import repair_directory
from utils import extract_frames_ffmpeg
from predictor import predict_labels, slice_video_by_sequence_incremental

def run_pipeline(video_dir, output_dir, logger=print, cancel_flag=lambda: False, process_list=None):

    logger("启动视频标准化处理...")
    repair_directory(video_dir)

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

def process_single_video(video_path, output_dir, index=0, total=1):
    """处理单个视频：抽帧 → 推理 → 切片，并按日志格式输出进度供 UI 更新"""
    print(f"开始处理视频 {index + 1}/{total}", flush=True)
    print(f"正在处理: {os.path.basename(video_path)}", flush=True)

    temp_dir = os.path.join(output_dir, "temp_frames")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps_orig     = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        target_fps = 2
        if total_frames > 0 and fps_orig > 0:
            total_extract = math.ceil(total_frames / fps_orig * target_fps)
        else:
            total_extract = 1

        last_pct = -1
        def frame_cb(frame_idx):
            nonlocal last_pct
            pct = min(100, int(frame_idx / total_extract * 100))
            if pct != last_pct:
                print(f"FrameProgress: {pct}%", flush=True)
                last_pct = pct

        extract_frames_ffmpeg(
            video_path=video_path,
            output_dir=temp_dir,
            fps=target_fps,
            width=640,
            progress_callback=frame_cb
        )
        if last_pct < 100:
            print("FrameProgress: 100%", flush=True)

        labels = predict_labels(
            temp_dir,
            batch_size=64,
            progress=True
        )

        slice_video_by_sequence_incremental(
            video_path=video_path,
            labels=labels,
            output_dir=output_dir,
            min_segment_sec=5,
            progress_callback=lambda p: print(f"SliceProgress: {p:.2f}%", flush=True)
        )

    except Exception as e:
        print(f"⚠️ 视频处理失败: {os.path.basename(video_path)}，原因: {e}", flush=True)
    finally:
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    parser = argparse.ArgumentParser(description="视频处理管道")
    parser.add_argument("--video_path",  required=True, help="待处理视频文件路径")
    parser.add_argument("--output_path", required=True, help="切片输出目录")
    parser.add_argument("--index",       type=int, default=0, help="当前序号")
    parser.add_argument("--total",       type=int, default=1, help="总视频数")
    args = parser.parse_args()

    process_single_video(
        video_path = args.video_path,
        output_dir = args.output_path,
        index      = args.index,
        total      = args.total
    )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="视频流水线主程序")
    parser.add_argument("--video_dir",  required=True, help="视频文件夹路径")
    parser.add_argument("--output_dir", required=True, help="输出切片目录")
    args = parser.parse_args()
    run_pipeline(args.video_dir, args.output_dir)
