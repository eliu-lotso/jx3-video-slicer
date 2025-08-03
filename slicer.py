import os
import cv2
import subprocess
import csv
import sys
import io
from config import FFMPEG_PATH

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
except Exception:
    pass

LABEL_MAP = {"map": 0, "loading": 1, "other": 2}

def slice_video_by_sequence_incremental(video_path, labels, output_dir, fps=2, min_segment_sec=5, progress_callback=None):
    """根据标签序列切割视频，导出片段和日志"""
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(video_path))[0]
    label_ids = [LABEL_MAP.get(l, 2) for l in labels]
    if not label_ids:
        print("无有效标签，跳过切片")
        return

    segments = []
    current_type = label_ids[0]
    start_idx = 0
    for i in range(1, len(label_ids)):
        if label_ids[i] != current_type:
            segments.append((current_type, start_idx, i - 1))
            current_type = label_ids[i]
            start_idx = i
    segments.append((current_type, start_idx, len(label_ids) - 1))

    FIGHTING = LABEL_MAP["map"]
    LOADING = LABEL_MAP["loading"]
    cuts = []
    i = 0
    while i < len(segments) - 3:
        types = [segments[i][0], segments[i+1][0], segments[i+2][0], segments[i+3][0]]
        if set(types) == {LOADING, FIGHTING}:
            cuts.append((segments[i][1], segments[i+3][2]))
            i += 4
        else:
            i += 1

    if not cuts:
        cuts.append((0, len(label_ids) - 1))
    else:
        last_end = cuts[-1][1]
        if last_end < len(label_ids) - 1:
            cuts.append((last_end + 1, len(label_ids) - 1))

    min_len = int(min_segment_sec * fps)
    merged = []
    for s, e in cuts:
        if not merged:
            merged.append((s, e))
        else:
            prev_s, prev_e = merged[-1]
            if (e - s + 1) < min_len:
                merged[-1] = (prev_s, e)
            else:
                merged.append((s, e))

    cap = cv2.VideoCapture(video_path)
    real_fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    log_path = os.path.join(output_dir, f"{base}_log.csv")
    with open(log_path, "w", newline="", encoding="utf-8") as logf:
        writer = csv.writer(logf)
        writer.writerow(["segment", "start_frame", "end_frame", "start_time", "duration_sec", "video_path"])
        for idx, (s, e) in enumerate(merged):
            start_sec = s / fps
            duration = (e - s + 1) / fps
            out_name = f"{base}_cut{idx:02d}.mp4"
            out_path = os.path.join(output_dir, out_name)
            cmd = [
                FFMPEG_PATH, "-y", "-ss", f"{start_sec:.2f}", "-i", video_path,
                "-t", f"{duration:.2f}", "-c", "copy", out_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            writer.writerow([idx, s, e, f"{start_sec:.2f}", f"{duration:.2f}", out_path])
            
            if progress_callback:
                progress_percent = (idx + 1) / len(merged) * 100
                progress_callback(progress_percent)
            else:
                print(f"SliceProgress: {int((idx+1)/len(merged)*100)}%", flush=True)

    print("切片完成", flush=True)
