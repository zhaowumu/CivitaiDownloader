from core.api import fetch_user_images
from core.storage import save_json, load_json
from core.diff import get_need_download
from core.downloader import download_all
from core.storage import load_cursor, save_cursor


class CivitaiSyncManager:

    def __init__(self, username, on_progress=None, on_stats=None):
        self.username = username
        self.on_progress = on_progress
        self.on_stats = on_stats

    def sync(self):
        start_url = load_cursor(self.username)

        remote_list, last_url = fetch_user_images(
            self.username,
            start_url=start_url
        )

        # 新拉到的数据
        remote = {i["id"]: i for i in remote_list}

        # 旧的本地数据
        local = load_json(self.username)

        # ===== 合并，保证不丢数据、不重复 =====
        merged = dict(local)
        merged.update(remote)

        # 计算真正需要下载的
        need = get_need_download(self.username, merged)

        if self.on_stats:
            self.on_stats(len(merged), len(local), len(need))

        # 保存完整数据
        save_json(self.username, merged)
        save_cursor(self.username, last_url)

        # 下载缺失文件
        download_all(
            self.username,
            need,
            progress_cb=self.on_progress
        )
