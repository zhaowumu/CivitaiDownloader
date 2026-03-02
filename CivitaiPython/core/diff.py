from pathlib import Path
from config import DATA_ROOT


def get_need_download(username, remote_data):
    """
    比较远程数据和本地文件，找出需要下载的图片
    
    功能说明：
    - 根据用户名和NSFW级别构建本地文件路径
    - 遍历远程数据中的每个图片信息
    - 检查本地是否已存在对应文件
    - 返回需要下载的图片信息列表
    
    参数：
    username (str): 用户名，用于构建本地存储路径
    remote_data (dict): 远程图片数据字典，键为图片ID，值为图片详细信息
    
    返回：
    list: 需要下载的图片信息列表
    """
    # 构建用户的本地数据根目录路径：DATA_ROOT/username
    base = Path(DATA_ROOT) / username
    # 初始化需要下载的图片列表
    need = []

    # 遍历远程数据字典中的每个图片
    for img_id, info in remote_data.items():
        # 获取图片的NSFW级别，如果没有则默认为"Normal"
        sub = str(info.get("nsfwLevel", "Normal"))
        # 获取图片的下载URL
        url = info.get("url")
        # 如果URL不存在，跳过该图片
        if not url:
            continue

        # 从URL中提取文件扩展名
        # 处理逻辑：先去掉URL参数(?)，再取最后一个点(.)后的部分
        # 与downloader.py保持一致
        ext = url.split("?")[0].rsplit(".", 1)[-1]
        if "/" in ext:
            ext = "jpg"
        # 构建完整的本地文件路径：DATA_ROOT/username/NSFW级别/图片ID.扩展名
        path = base / sub / f"{img_id}.{ext}"

        # 检查文件是否已存在，如果不存在则添加到需要下载列表
        if not path.exists():
            need.append(info)

    # 返回需要下载的图片信息列表
    return need
