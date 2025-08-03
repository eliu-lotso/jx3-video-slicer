import cv2
import math
import os
import argparse
import shutil

from utils import extract_frames_ffmpeg
from predictor import predict_labels
from slicer import slice_video_by_sequence_incremental

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
    parser = argparse.ArgumentParser(description="子进程：单视频处理")
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
    main()
