import os
import time
import torch
import torchvision.transforms as transforms
from PIL import Image
import timm
import cv2
import subprocess
import csv
import sys
import io
from config import MODEL_DIR, FFMPEG_PATH

CLASS_NAMES = ["loading", "map", "other"]
LABEL_MAP = {"map": 0, "loading": 1, "other": 2}

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
except Exception:
    pass

def load_model_timm(model_name, model_path, device):
    """使用 timm 创建模型并加载指定权重"""
    model = timm.create_model(model_name, pretrained=False, num_classes=len(CLASS_NAMES))
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model

def predict_labels(image_dir, batch_size=64, progress=True):
    """对目录下图片批量推理，返回标签列表"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model_configs = [
        ("efficientnet_b0", os.path.join(MODEL_DIR, "efficientnet_b0.pth")),
        ("mobilenetv3_large_100", os.path.join(MODEL_DIR, "mobilenetv3_large.pth")),
        ("ghostnet_100", os.path.join(MODEL_DIR, "ghostnet.pth"))
    ]

    models_loaded = [load_model_timm(name, path, device) for name, path in model_configs]

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith(".jpg")])
    labels = []
    total = len(image_files)
    
    for i in range(0, total, batch_size):
        batch_files = image_files[i:i + batch_size]
        images = [transform(Image.open(os.path.join(image_dir, f)).convert("RGB")) for f in batch_files]
        input_tensor = torch.stack(images).to(device)

        votes = torch.zeros(len(batch_files), len(CLASS_NAMES), device=device)
        with torch.no_grad():
            for model in models_loaded:
                outputs = model(input_tensor)
                votes += torch.nn.functional.softmax(outputs, dim=1)

        preds = torch.argmax(votes, dim=1).cpu().tolist()
        for p in preds:
            labels.append(CLASS_NAMES[p])

        if progress:
            percent = int((i + len(batch_files)) / total * 100)
            print(f"InferenceProgress: {percent}%", flush=True)
            time.sleep(0.01)

    return labels

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
