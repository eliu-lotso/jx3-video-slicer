# 剑网三花舞剑竞技场视频切片工具

一个专门用于剑网三花舞剑竞技场视频智能切片的工具，基于深度学习自动识别游戏场景并进行视频分割。

## 功能特点

- 🎯 **智能场景识别**: 使用多个深度学习模型识别游戏中的不同场景（加载画面、地图场景、其他场景）
- ✂️ **自动视频切片**: 根据场景变化自动分割视频，提取竞技场对战片段
- 🎮 **花舞剑专用**: 针对剑网三花舞剑竞技场视频优化
- 🖥️ **图形界面**: 提供友好的PyQt5图形界面
- ⚡ **GPU加速**: 支持CUDA加速推理
- 📊 **进度显示**: 实时显示处理进度

## 系统要求

- Python 3.8+
- CUDA支持的GPU（推荐）
- FFmpeg

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/eliu-lotso/jx3-video-slicer.git
cd jx3-video-slicer
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 下载预训练模型：
   - 将模型文件放入 `models/` 目录
   - 确保包含以下文件：
     - `efficientnet_b0.pth`
     - `mobilenetv3_large.pth`
     - `ghostnet.pth`

## 使用方法

### 图形界面
```bash
python video_slicer_ui.py
```

### 命令行
```bash
python pipeline_main.py
```

## 项目结构

```
JX3-cut/
├── video_slicer_ui.py      # 图形界面
├── pipeline_main.py        # 主处理流程
├── pipeline_worker.py      # 单视频处理
├── predictor.py           # AI模型推理
├── slicer.py              # 视频切片逻辑
├── utils.py               # 工具函数
├── repair_videos.py       # 视频修复
├── config.py              # 配置文件
├── requirements.txt       # 依赖包
├── bin/                   # FFmpeg可执行文件
│   ├── ffmpeg.exe
│   └── ffprobe.exe
└── models/                # 预训练模型
    ├── efficientnet_b0.pth
    ├── mobilenetv3_large.pth
    └── ghostnet.pth
```

## 工作原理

1. **视频标准化**: 修复和标准化输入视频
2. **帧提取**: 使用FFmpeg从视频中提取帧（2fps）
3. **AI识别**: 使用三个深度学习模型对帧进行分类
4. **智能切片**: 根据场景类型自动分割视频
5. **输出整理**: 将切片后的视频保存到指定目录

## 模型说明

- **EfficientNet-B0**: 高效的CNN模型
- **MobileNetV3-Large**: 轻量级移动端模型
- **GhostNet**: 高效的Ghost模块网络

三个模型通过投票机制确定最终分类结果，提高识别准确性。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持剑网三花舞剑竞技场视频切片
- 集成多个深度学习模型
- 提供图形界面 