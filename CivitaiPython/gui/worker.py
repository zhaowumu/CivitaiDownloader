from PyQt5.QtCore import QThread, pyqtSignal
from core.sync import CivitaiSyncManager
import traceback


class SyncWorker(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    stats = pyqtSignal(int, int, int)

    def __init__(self, username):
        super().__init__()
        self.username = username

    def run(self):
        try:
            self.log.emit(f"开始同步: {self.username}")
            self.log.emit("正在拉取远端图片列表...")

            def on_progress(done, total):
                self.progress.emit(done, total)

            def on_stats(remote, local, need):
                self.stats.emit(remote, local, need)

            manager = CivitaiSyncManager(
                self.username,
                on_progress=on_progress,
                on_stats=on_stats
            )

            manager.sync()
            self.log.emit("下载完成")
            self.finished.emit()

        except Exception:
            self.error.emit(traceback.format_exc())
