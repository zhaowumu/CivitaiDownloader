from pathlib import Path
from config import DATA_ROOT


def get_need_download(username, remote_data):
    base = Path(DATA_ROOT) / username
    need = []

    for img_id, info in remote_data.items():
        sub = str(info.get("nsfwLevel", "Normal"))
        url = info.get("url")
        if not url:
            continue

        ext = url.split("?")[0].split(".")[-1]
        path = base / sub / f"{img_id}.{ext}"

        if not path.exists():
            need.append(info)

    return need
