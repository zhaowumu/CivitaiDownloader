import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import DATA_ROOT, MAX_WORKERS


def _download_one(username, info):
    url = info["url"]
    img_id = info["id"]
    sub = str(info.get("nsfwLevel", "Normal"))

    ext = url.split("?")[0].split(".")[-1]
    folder = Path(DATA_ROOT) / username / sub
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{img_id}.{ext}"
    if path.exists():
        return

    r = requests.get(
        url,
        timeout=60,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    r.raise_for_status()

    with open(path, "wb") as f:
        f.write(r.content)


def download_all(username, need_list, progress_cb=None):
    total = len(need_list)
    done = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [
            pool.submit(_download_one, username, info)
            for info in need_list
        ]

        for _ in as_completed(futures):
            done += 1
            if progress_cb:
                progress_cb(done, total)
