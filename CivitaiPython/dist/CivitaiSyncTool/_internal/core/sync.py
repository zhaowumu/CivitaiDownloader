from core.api import fetch_user_images
from core.storage import save_json, load_json, load_cursor, save_cursor
from core.diff import get_need_download
from core.downloader import download_all


class CivitaiSyncManager:

    def __init__(self, username, on_progress=None, on_stats=None, on_json_progress=None):
        self.username = username
        self.on_progress = on_progress
        self.on_stats = on_stats
        self.on_json_progress = on_json_progress # JSON 同步进度的回调

    def sync_json(self):
        """仅同步 JSON 数据"""
        start_url = load_cursor(self.username)

        remote_list, last_url = fetch_user_images(
            self.username,
            start_url=start_url,
            on_page_fetched=self.on_json_progress # 接入 API 回调
        )

        remote = {i["id"]: i for i in remote_list}
        local = load_json(self.username)

        # 合并
        merged = dict(local)
        merged.update(remote)

        save_json(self.username, merged)
        save_cursor(self.username, last_url)

        return merged

    def sync_download(self):
        """仅执行下载（基于现有 JSON）"""
        merged = load_json(self.username)
        need = get_need_download(self.username, merged)

        if self.on_stats:
            self.on_stats(len(merged), 0, len(need))

        download_all(
            self.username,
            need,
            progress_cb=self.on_progress
        )

    def sync_all(self):
        """全流程"""
        merged = self.sync_json()
        need = get_need_download(self.username, merged)

        if self.on_stats:
            self.on_stats(len(merged), 0, len(need))

        download_all(
            self.username,
            need,
            progress_cb=self.on_progress
        )