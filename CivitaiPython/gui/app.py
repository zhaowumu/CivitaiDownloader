import os
import sys
import platform
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QProgressBar, QScrollArea, QFrame, QMessageBox,
    QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal

from gui.worker import SyncWorker
from core.following import get_all_following_usernames
from core.storage import user_dir, list_local_users, get_user_stats
from config import MY_CIVITAI_NAME


class UserWidget(QFrame):
    """
    单个用户的 UI 卡片组件
    """
    req_sync_json = pyqtSignal(str)
    req_download = pyqtSignal(str)
    req_open_folder = pyqtSignal(str)

    def __init__(self, username, index=0, parent=None):
        super().__init__(parent)
        self.username = username
        self.setFrameShape(QFrame.StyledPanel)

        # 视觉分割：增加交替背景色（斑马纹）
        bg_color = "#ffffff" if index % 2 == 0 else "#f4f4f4"
        self.setStyleSheet(f"UserWidget {{ background-color: {bg_color}; border-bottom: 1px solid #ddd; }}")
        self.setFixedHeight(95)

        main_layout = QHBoxLayout(self)
        info_layout = QVBoxLayout()

        self.lbl_name = QLabel(f"<b>{username}</b>")
        self.lbl_name.setStyleSheet("font-size: 14px; background: transparent;")

        self.lbl_stats = QLabel("读取中...")
        self.lbl_stats.setStyleSheet("color: #666; background: transparent;")

        self.lbl_status = QLabel("就绪")
        self.lbl_status.setStyleSheet("color: #005fb8; font-size: 11px; font-weight: bold; background: transparent;")

        info_layout.addWidget(self.lbl_name)
        info_layout.addWidget(self.lbl_stats)
        info_layout.addWidget(self.lbl_status)
        info_layout.addStretch()

        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedWidth(200)
        self.progress.hide()

        btn_layout = QVBoxLayout()
        top_btn_layout = QHBoxLayout()
        self.btn_json = QPushButton("同步Json")
        self.btn_dl = QPushButton("只下载")
        top_btn_layout.addWidget(self.btn_json)
        top_btn_layout.addWidget(self.btn_dl)

        self.btn_folder = QPushButton("打开文件夹")
        btn_layout.addLayout(top_btn_layout)
        btn_layout.addWidget(self.btn_folder)

        main_layout.addLayout(info_layout, stretch=1)
        main_layout.addWidget(self.progress)
        main_layout.addLayout(btn_layout)

        self.btn_json.clicked.connect(lambda: self.req_sync_json.emit(self.username))
        self.btn_dl.clicked.connect(lambda: self.req_download.emit(self.username))
        self.btn_folder.clicked.connect(lambda: self.req_open_folder.emit(self.username))

        self.refresh_stats()

    def refresh_stats(self):
        """刷新 Json 数和下载数"""
        try:
            j_count, f_count = get_user_stats(self.username)
            self.lbl_stats.setText(f"Json: {j_count} | 已下载: {f_count}")
        except Exception:
            self.lbl_stats.setText("统计失败")

    def set_running(self, is_running, mode_text=""):
        self.btn_json.setEnabled(not is_running)
        self.btn_dl.setEnabled(not is_running)

        if is_running:
            self.lbl_status.setText(f"正在{mode_text}...")
            if mode_text == "download":
                self.progress.show()
                self.progress.setValue(0)
        else:
            self.progress.hide()
            self.lbl_status.setText("就绪")

    def update_json_count(self, count):
        """更新同步 JSON 时的数量"""
        self.lbl_status.setText(f"正在获取: {count} 条记录...")

    def update_progress(self, done, total):
        self.progress.setMaximum(total)
        self.progress.setValue(done)
        self.lbl_status.setText(f"进度: {done}/{total}")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Civitai 高级同步工具")
        self.resize(950, 750)

        # 核心布局
        layout = QVBoxLayout()

        # --- 顶部控制栏 ---
        top_layout = QHBoxLayout()

        self.btn_refresh_list = QPushButton("刷新列表")
        self.btn_refresh_list.clicked.connect(self.load_user_list)

        self.btn_fetch_follow = QPushButton("获取关注列表(API)")
        self.btn_fetch_follow.clicked.connect(self.fetch_following_users)

        self.btn_sync_all_json = QPushButton("一键同步所有JSON")
        self.btn_sync_all_json.clicked.connect(self.batch_sync_json)

        self.btn_download_all = QPushButton("一键下载所有缺失")
        self.btn_download_all.clicked.connect(self.batch_download)

        top_layout.addWidget(self.btn_refresh_list)
        top_layout.addWidget(self.btn_fetch_follow)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_sync_all_json)
        top_layout.addWidget(self.btn_download_all)

        layout.addLayout(top_layout)

        # --- 中间滚动列表区域 ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(0)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        # --- 底部日志条 ---
        self.lbl_global_status = QLabel("Ready.")
        layout.addWidget(self.lbl_global_status)

        self.setLayout(layout)

        # 状态管理
        self.user_widgets = {}
        self.workers = {}
        self.queue = []
        self.is_processing_queue = False

        self.load_user_list()

    # ==========================
    # 核心业务逻辑
    # ==========================
    def load_user_list(self):
        """扫描本地目录并加载用户卡片"""
        # 清空现有
        for i in reversed(range(self.container_layout.count())):
            w = self.container_layout.itemAt(i).widget()
            if w: w.deleteLater()

        self.user_widgets.clear()

        users = list_local_users()
        for idx, u in enumerate(users):
            self.add_user_widget(u, idx)

        self.lbl_global_status.setText(f"加载了 {len(users)} 个用户")

    def add_user_widget(self, username, index=0):
        if username in self.user_widgets:
            return

        w = UserWidget(username, index)
        w.req_sync_json.connect(self.handle_sync_json)
        w.req_download.connect(self.handle_download)
        w.req_open_folder.connect(self.handle_open_folder)

        self.container_layout.addWidget(w)
        self.user_widgets[username] = w

    def fetch_following_users(self):
        """实现遗漏的关注列表获取逻辑"""
        self.lbl_global_status.setText("正在通过 API 获取关注列表...")
        QApplication.processEvents()  # 强制刷新 UI 显示

        try:
            names = get_all_following_usernames(MY_CIVITAI_NAME)
            new_count = 0
            for n in names:
                # user_dir 内部会自动创建文件夹
                path = user_dir(n)
                # 简单判断是否是刚创建的（如果之前没 data.json 且没子目录，可视为新用户）
                # 这里为了简单直接根据 names 刷新

            self.load_user_list()
            QMessageBox.information(self, "完成", f"已同步关注列表。\n当前总计关注用户: {len(names)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取失败: {str(e)}")

        self.lbl_global_status.setText("Ready.")

    def handle_open_folder(self, username):
        path = str(user_dir(username).absolute())
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def handle_sync_json(self, username):
        self.start_worker(username, "json")

    def handle_download(self, username):
        self.start_worker(username, "download")

    # ==========================
    # 队列与批量处理
    # ==========================
    def batch_sync_json(self):
        users = list_local_users()
        for u in users:
            self.queue.append((u, "json"))
        self.process_queue()

    def batch_download(self):
        users = list_local_users()
        for u in users:
            self.queue.append((u, "download"))
        self.process_queue()

    def process_queue(self):
        if self.is_processing_queue:
            return

        if not self.queue:
            self.lbl_global_status.setText("批量任务完成")
            return

        self.is_processing_queue = True
        username, mode = self.queue.pop(0)

        if username in self.user_widgets:
            self.scroll.ensureWidgetVisible(self.user_widgets[username])

        self.start_worker(username, mode, is_queue=True)

    def start_worker(self, username, mode, is_queue=False):
        if username in self.workers:
            if is_queue:
                self.is_processing_queue = False
                self.process_queue()
            return

        if username in self.user_widgets:
            self.user_widgets[username].set_running(True, mode)

        worker = SyncWorker(username, mode)
        worker.log.connect(lambda msg: self.lbl_global_status.setText(f"[{username}] {msg}"))

        if username in self.user_widgets:
            w = self.user_widgets[username]
            worker.progress.connect(w.update_progress)
            worker.json_count_update.connect(w.update_json_count)
            worker.data_updated.connect(w.refresh_stats)

        worker.finished.connect(lambda: self.on_worker_finished(username, is_queue))
        worker.error.connect(lambda err: print(f"Error {username}: {err}"))

        self.workers[username] = worker
        worker.start()

    def on_worker_finished(self, username, is_queue):
        if username in self.workers:
            del self.workers[username]

        if username in self.user_widgets:
            self.user_widgets[username].set_running(False)
            self.user_widgets[username].refresh_stats()

        if is_queue:
            self.is_processing_queue = False
            self.process_queue()