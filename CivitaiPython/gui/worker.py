from PyQt5.QtCore import QThread, pyqtSignal
from core.sync import CivitaiSyncManager
import traceback


class SyncWorker(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)  # done, total
    stats = pyqtSignal(int, int, int)  # remote_count, local_count, need_dl

    # 新增: 同步 JSON 时的数量变化信号
    json_count_update = pyqtSignal(int)
    data_updated = pyqtSignal()

    def __init__(self, username, mode="all"):
        super().__init__()
        self.username = username
        self.mode = mode

    def run(self):
        try:
            self.log.emit(f"[{self.username}] 任务开始: {self.mode}")

            def on_progress(done, total):
                self.progress.emit(done, total)

            def on_stats(remote, local, need):
                self.stats.emit(remote, local, need)

            def on_json_progress(count):
                self.json_count_update.emit(count)

            manager = CivitaiSyncManager(
                self.username,
                on_progress=on_progress,
                on_stats=on_stats,
                on_json_progress=on_json_progress
            )

            if self.mode == "json":
                manager.sync_json()
                self.log.emit(f"[{self.username}] JSON 更新完毕")

            elif self.mode == "download":
                manager.sync_download()
                self.log.emit(f"[{self.username}] 下载完毕")

            else:  # all
                manager.sync_all()
                self.log.emit(f"[{self.username}] 全部同步完毕")

            self.data_updated.emit()
            self.finished.emit()

        except Exception:
            self.error.emit(traceback.format_exc())