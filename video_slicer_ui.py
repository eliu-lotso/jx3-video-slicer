import sys
import os
import re

try:
    import psutil
except ImportError:
    psutil = None

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog,
    QLineEdit, QProgressBar, QTextEdit
)
from PyQt5.QtCore import QThread, pyqtSignal

try:
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
        sys.path.append(base_dir)
    else:
        base_dir = os.path.dirname(__file__)
    from pipeline_main import run_pipeline
except Exception as e:
    print(f"模块导入失败: {e}")
    raise


class VideoProcessingThread(QThread):
    log_signal = pyqtSignal(str)
    stage_signal = pyqtSignal(str)
    frame_progress_signal = pyqtSignal(int)
    inference_progress_signal = pyqtSignal(int)
    slice_progress_signal = pyqtSignal(int)

    def __init__(self, video_dir, output_dir):
        super().__init__()
        self.processes = []  # 用于存储子进程
        self.video_dir = video_dir
        self.output_dir = output_dir
        self._stopped = False

    def run(self):
        def emit_log(msg):
            if self._stopped:
                return
            self.log_signal.emit(msg)

            if "正在处理" in msg:
                self.stage_signal.emit("读取视频中")
            elif "正在执行命令" in msg:
                self.stage_signal.emit("抽帧中")
            elif "模型推理中" in msg:
                self.stage_signal.emit("模型推理中")
            elif "切片完成" in msg:
                self.stage_signal.emit("切片完成")

            match_frame = re.search(r"FrameProgress[:：]\s*(\d+)%", msg)
            if match_frame:
                self.frame_progress_signal.emit(int(match_frame.group(1)))

            match_infer = re.search(r"InferenceProgress[:：]\s*(\d+)%", msg)
            if match_infer:
                self.inference_progress_signal.emit(int(match_infer.group(1)))

            match_slice = re.search(r"SliceProgress[:：]\s*(\d+)%", msg)
            if match_slice:
                self.slice_progress_signal.emit(int(match_slice.group(1)))

        try:
            run_pipeline(
                self.video_dir,
                self.output_dir,
                logger=emit_log,
                cancel_flag=lambda: self._stopped,
                process_list=self.processes
            )
        except Exception as e:
            emit_log(f"❌ 线程异常: {str(e)}")
        finally:
            self.stage_signal.emit("任务已取消")
            self.frame_progress_signal.emit(0)
            self.inference_progress_signal.emit(0)
            self.slice_progress_signal.emit(0)
            self.log_signal.emit("❌ 任务被强制取消或中断。")

    def stop(self):
        self._stopped = True
        if psutil:
            for p in getattr(self, "processes", []):
                try:
                    proc = psutil.Process(p.pid)
                    for child in proc.children(recursive=True):
                        child.kill()
                    proc.kill()
                except Exception as e:
                    print(f"终止进程失败: {e}")
        else:
            print("⚠️ 未安装 psutil，无法自动终止子进程")


class VideoSlicerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("剑网三竞技场CUT（知愿愿）")
        self.resize(700, 520)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.video_path_btn = QPushButton("选择视频文件夹")
        self.video_path_btn.clicked.connect(self.select_video_folder)
        self.video_path_input = QLineEdit()

        self.output_path_btn = QPushButton("选择输出目录")
        self.output_path_btn.clicked.connect(self.select_output_folder)
        self.output_path_input = QLineEdit()

        self.run_btn = QPushButton("▶️ 开始处理")
        self.run_btn.clicked.connect(self.start_processing)

        self.cancel_btn = QPushButton("⛔ 取消任务")
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)

        self.status_label = QLabel("等待开始...")

        self.frame_progress = QProgressBar()
        self.frame_progress.setFormat("抽帧进度：%p%")

        self.infer_progress = QProgressBar()
        self.infer_progress.setFormat("推理进度：%p%")

        self.slice_progress = QProgressBar()
        self.slice_progress.setFormat("切片进度：%p%")

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        layout.addWidget(self.video_path_btn)
        layout.addWidget(self.video_path_input)
        layout.addWidget(self.output_path_btn)
        layout.addWidget(self.output_path_input)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.frame_progress)
        layout.addWidget(self.infer_progress)
        layout.addWidget(self.slice_progress)
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("日志输出:"))
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def select_video_folder(self):
        path = QFileDialog.getExistingDirectory(self, "选择视频目录")
        if path:
            self.video_path_input.setText(path)

    def select_output_folder(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_path_input.setText(path)

    def start_processing(self):
        video_dir = self.video_path_input.text().strip()
        output_dir = self.output_path_input.text().strip()

        self.thread = VideoProcessingThread(video_dir, output_dir)
        self.thread.log_signal.connect(self.log_output.append)
        self.thread.stage_signal.connect(self.status_label.setText)
        self.thread.frame_progress_signal.connect(self.frame_progress.setValue)
        self.thread.inference_progress_signal.connect(self.infer_progress.setValue)
        self.thread.slice_progress_signal.connect(self.slice_progress.setValue)

        self.status_label.setText("准备处理...")
        self.frame_progress.setValue(0)
        self.infer_progress.setValue(0)
        self.slice_progress.setValue(0)
        self.log_output.clear()
        self.cancel_btn.setEnabled(True)

        self.thread.start()

    def cancel_processing(self):
        if hasattr(self, "thread") and self.thread:
            self.thread.stop()
            self.status_label.setText("任务取消中...")


def main():
    app = QApplication(sys.argv)
    window = VideoSlicerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
