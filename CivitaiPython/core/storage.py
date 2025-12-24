import json
from pathlib import Path
from config import DATA_ROOT


def user_dir(username):
    path = Path(DATA_ROOT) / username
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_local_users():
    root = Path(DATA_ROOT)
    if not root.exists():
        return []
    return sorted([
        p.name for p in root.iterdir()
        if p.is_dir()
    ])


def save_json(username, data_dict):
    path = user_dir(username) / "data.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {"images": list(data_dict.values())},
            f,
            indent=2,
            ensure_ascii=False
        )


def load_json(username):
    path = user_dir(username) / "data.json"
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)

    return {i["id"]: i for i in obj.get("images", [])}


def load_cursor(username):
    path = user_dir(username) / "cursor.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return None


def save_cursor(username, url):
    path = user_dir(username) / "cursor.txt"
    path.write_text(url or "", encoding="utf-8")
