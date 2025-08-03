import os
import time
import torch
import torchvision.transforms as transforms
from PIL import Image
import timm
from config import MODEL_DIR

CLASS_NAMES = ["loading", "map", "other"]

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
