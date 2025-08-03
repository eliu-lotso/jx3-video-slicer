# GitHub 上传指南

## 准备工作

1. **创建GitHub仓库**
   - 访问 https://github.com/new
   - 仓库名称: `jx3-video-slicer`
   - 描述: `剑网三花舞剑竞技场视频智能切片工具`
   - 选择 Public
   - 不要初始化README（已存在）

## 上传步骤

### 1. 初始化Git仓库
```bash
git init
git add .
git commit -m "Initial commit: 剑网三花舞剑竞技场视频切片工具 v1.0.0"
```

### 2. 添加远程仓库
```bash
git remote add origin https://github.com/yourusername/jx3-video-slicer.git
```

### 3. 推送到GitHub
```bash
git branch -M main
git push -u origin main
```

## 发布版本

### 1. 创建发布包
```bash
python release.py
```

### 2. 在GitHub上创建Release
1. 访问仓库页面
2. 点击 "Releases"
3. 点击 "Create a new release"
4. 标签: `v1.0.0`
5. 标题: `剑网三花舞剑竞技场视频切片工具 v1.0.0`
6. 描述: 复制README.md内容
7. 上传 `jx3-video-slicer-v1.0.0.zip`

## 注意事项

- 确保 `.gitignore` 正确配置，避免上传大文件
- 模型文件（.pth）和FFmpeg可执行文件较大，可能需要使用Git LFS
- 如果文件过大，考虑分开发布模型文件

## 后续维护

- 定期更新依赖版本
- 添加新功能和修复bug
- 更新文档和示例 