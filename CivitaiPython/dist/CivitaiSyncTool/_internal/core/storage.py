import json
import os
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

    # 兼容处理
    images = obj.get("images", [])
    if isinstance(images, dict):
        return images

    return {i["id"]: i for i in images}


def load_cursor(username):
    path = user_dir(username) / "cursor.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return None


def save_cursor(username, url):
    path = user_dir(username) / "cursor.txt"
    path.write_text(url or "", encoding="utf-8")


def get_user_stats(username):
    """
    计算并返回 (JSON记录数, 本地实际文件数)
    """
    # 1. 获取 JSON 中的图片记录数量
    data = load_json(username)
    json_count = len(data)

    # 2. 统计文件夹下实际存在的图片文件数量
    path = user_dir(username)
    file_count = 0
    # 定义图片和视频后缀
    valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.mp4', '.gif'}

    # 递归查找所有文件
    if path.exists():
        for p in path.rglob("*"):
            if p.is_file() and p.suffix.lower() in valid_exts:
                file_count += 1

    return json_count, file_count