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

        remote = {i["id"]: i for i in remote_list}
        local = load_json(self.username)
        need = get_need_download(self.username, remote)

        if self.on_stats:
            self.on_stats(len(remote), len(local), len(need))

        save_json(self.username, remote)
        save_cursor(self.username, last_url)

        download_all(
            self.username,
            need,
            progress_cb=self.on_progress
        )
