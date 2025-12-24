from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QLabel, QListWidget, QProgressBar
)

from gui.worker import SyncWorker
from core.following import get_all_following_usernames
from core.storage import user_dir, list_local_users
from config import MY_CIVITAI_NAME


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Civitai 批量同步工具")
        self.resize(800, 600)

        self.worker = None
        self.user_queue = []

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("（已弃用）手动输入用户名")

        self.add_btn = QPushButton("获取关注列表")
        self.add_btn.clicked.connect(self.fetch_following)

        self.user_list = QListWidget()

        self.start_btn = QPushButton("开始同步全部")
        self.start_btn.clicked.connect(self.start_batch)

        self.stats_label = QLabel("远端: 0 | 本地: 0 | 待下载: 0")
        self.progress = QProgressBar()

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        top = QHBoxLayout()
        top.addWidget(self.user_input)
        top.addWidget(self.add_btn)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.user_list)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.log_view)

        self.setLayout(layout)

        self.refresh_user_list()

    # ==========================
    # 关注列表 -> 创建用户目录（稳定版）
    # ==========================
    def fetch_following(self):
        self.log("同步关注列表...")

        try:
            usernames = get_all_following_usernames(MY_CIVITAI_NAME)

            total = 0
            for username in usernames:
                user_dir(username)
                total += 1

            self.refresh_user_list()
            self.log(f"已导入 {total} 个关注用户")

        except Exception as e:
            self.log(str(e))

    # ==========================
    # 目录即用户源
    # ==========================
    def refresh_user_list(self):
        self.user_list.clear()
        for name in list_local_users():
            self.user_list.addItem(name)

    # ==========================
    # 批量同步
    # ==========================
    def start_batch(self):
        self.user_queue = list_local_users()
        if not self.user_queue:
            return

        self.start_btn.setEnabled(False)
        self.log_view.clear()
        self._sync_next()

    def _sync_next(self):
        if not self.user_queue:
            self.start_btn.setEnabled(True)
            self.log("全部同步完成")
            return

        username = self.user_queue.pop(0)
        self.log(f"==== 同步用户 {username} ====")

        self.worker = SyncWorker(username)
        self.worker.log.connect(self.log)
        self.worker.stats.connect(self.update_stats)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self._sync_next)
        self.worker.start()

    def update_stats(self, remote, local, need):
        self.stats_label.setText(
            f"远端: {remote} | 本地: {local} | 待下载: {need}"
        )
        self.progress.setMaximum(max(need, 1))
        self.progress.setValue(0)

    def update_progress(self, done, total):
        self.progress.setMaximum(total)
        self.progress.setValue(done)

    def log(self, msg):
        self.log_view.append(msg)
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )
