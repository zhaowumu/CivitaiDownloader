import json
import os
import re
from pathlib import Path
from config import DATA_ROOT


def validate_username(username):
    """
    验证用户名是否合法
    
    功能说明：
    - 检查用户名是否为空
    - 检查用户名长度
    - 检查是否包含非法字符
    
    参数：
    username (str): 用户名
    
    返回：
    bool: 用户名是否合法
    """
    if not username or not isinstance(username, str):
        return False
    
    # 检查长度
    if len(username) < 1 or len(username) > 50:
        return False
    
    # 检查是否包含非法字符（只允许字母、数字、下划线、连字符）
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, username):
        return False
    
    return True


def user_dir(username):
    """
    创建并返回指定用户的本地存储目录
    
    功能说明：
    - 根据用户名构建本地存储路径
    - 自动创建不存在的目录（包括父目录）
    - 如果目录已存在，不会抛出异常
    - 包含输入验证
    
    参数：
    username (str): 用户名
    
    返回：
    Path: 用户存储目录的Path对象
    
    异常：
    ValueError: 当用户名无效时抛出
    """
    # 验证用户名
    if not validate_username(username):
        raise ValueError(f"无效的用户名: {username}")
    
    # 构建用户目录路径：DATA_ROOT/username
    path = Path(DATA_ROOT) / username
    # 创建目录（如果不存在），parents=True表示创建所有必要的父目录
    # exist_ok=True表示如果目录已存在，不会抛出异常
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_local_users():
    """
    列出本地存储中所有的用户目录
    
    功能说明：
    - 检查DATA_ROOT目录是否存在
    - 遍历目录下所有子目录
    - 返回排序后的用户名列表
    
    返回：
    list[str]: 用户名列表
    """
    # 获取数据根目录的Path对象
    root = Path(DATA_ROOT)
    # 如果根目录不存在，返回空列表
    if not root.exists():
        return []
    # 遍历根目录下所有子目录，返回排序后的目录名列表
    return sorted([
        p.name for p in root.iterdir()  # 获取目录名
        if p.is_dir()  # 只包含目录
    ])


def save_json(username, data_dict):
    """
    保存用户的图片数据到JSON文件
    
    功能说明：
    - 将图片数据字典保存为JSON格式
    - 数据格式为{"images": [图片列表]}
    - 使用UTF-8编码，确保中文等特殊字符正确保存
    
    参数：
    username (str): 用户名
    data_dict (dict): 图片数据字典，键为图片ID，值为图片详细信息
    """
    # 获取用户目录下的data.json文件路径
    path = user_dir(username) / "data.json"
    # 以UTF-8编码写入文件
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {"images": list(data_dict.values())},  # 转换为{"images": [图片列表]}格式
            f,
            indent=2,  # 缩进2个空格，提高可读性
            ensure_ascii=False  # 不转义非ASCII字符
        )


def load_json(username):
    """
    从JSON文件加载用户的图片数据
    
    功能说明：
    - 加载用户的data.json文件
    - 处理不同格式的数据（兼容旧版本）
    - 返回以图片ID为键的字典格式
    
    参数：
    username (str): 用户名
    
    返回：
    dict: 图片数据字典，键为图片ID，值为图片详细信息
    """
    # 获取用户目录下的data.json文件路径
    path = user_dir(username) / "data.json"
    # 如果文件不存在，返回空字典
    if not path.exists():
        return {}

    # 以UTF-8编码读取文件
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)

    # 兼容处理：支持不同格式的数据结构
    images = obj.get("images", [])
    # 如果images已经是字典格式，直接返回
    if isinstance(images, dict):
        return images

    # 否则将列表转换为字典，以图片ID为键
    return {i["id"]: i for i in images}


def load_cursor(username):
    """
    加载用户的下载进度游标
    
    功能说明：
    - 读取用户的cursor.txt文件
    - 该文件存储了最后一次下载的分页URL
    - 用于断点续传功能
    
    参数：
    username (str): 用户名
    
    返回：
    str or None: 最后一次下载的分页URL，如果文件不存在则返回None
    """
    # 获取用户目录下的cursor.txt文件路径
    path = user_dir(username) / "cursor.txt"
    # 如果文件存在，读取内容并去除首尾空白字符
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    # 文件不存在，返回None
    return None


def save_cursor(username, url):
    """
    保存用户的下载进度游标
    
    功能说明：
    - 将分页URL写入cursor.txt文件
    - 用于断点续传功能
    - 支持保存None或空字符串
    
    参数：
    username (str): 用户名
    url (str or None): 分页URL，None或空字符串表示重置游标
    """
    # 获取用户目录下的cursor.txt文件路径
    path = user_dir(username) / "cursor.txt"
    # 写入URL，如果URL为None则写入空字符串
    path.write_text(url or "", encoding="utf-8")


def get_user_stats(username):
    """
    计算并返回用户的统计信息
    
    功能说明：
    - 获取JSON文件中的图片记录数量
    - 统计本地实际存在的图片文件数量
    - 支持多种图片和视频格式
    
    参数：
    username (str): 用户名
    
    返回：
    tuple: (JSON记录数, 本地实际文件数)
    """
    # 1. 获取JSON中的图片记录数量
    data = load_json(username)
    json_count = len(data)

    # 2. 统计文件夹下实际存在的图片文件数量
    path = user_dir(username)
    file_count = 0
    # 定义有效的图片和视频文件扩展名
    valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.mp4', '.gif'}

    # 递归查找所有文件
    if path.exists():
        for p in path.rglob("*"):  # 递归遍历所有子目录和文件
            # 如果是文件且扩展名在有效列表中
            if p.is_file() and p.suffix.lower() in valid_exts:
                file_count += 1

    # 返回(JSON记录数, 本地实际文件数)
    return json_count, file_count