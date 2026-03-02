import requests
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import DATA_ROOT, MAX_WORKERS, REQUEST_DELAY


def _download_one(username, info, max_retries=3):
    """
    下载单个图片到本地
    
    功能说明：
    - 根据图片信息下载单个图片文件
    - 自动创建存储目录（基于用户名和NSFW级别）
    - 跳过已存在的文件
    - 设置合理的超时时间和用户代理
    - 支持自动重试机制，避免网络波动导致下载失败
    
    参数：
    username (str): 用户名，用于构建存储路径
    info (dict): 图片信息字典，包含url、id、nsfwLevel等字段
    max_retries (int): 最大重试次数，默认3次
    
    返回：
    bool: 下载是否成功
    """
    # 获取图片下载URL
    url = info["url"]
    # 获取图片ID
    img_id = info["id"]
    # 获取图片NSFW级别，默认值为"Normal"
    sub = str(info.get("nsfwLevel", "Normal"))

    # 从URL中提取文件扩展名
    # 处理逻辑：先去掉URL参数(?)，再取最后一个点(.)后的部分
    # 提取扩展名，带兜底
    ext = url.split("?")[0].rsplit(".", 1)[-1]
    if "/" in ext:
        ext = "jpg"

    # 构建存储目录路径：DATA_ROOT/username/NSFW级别
    folder = Path(DATA_ROOT) / username / sub
    # 确保目录存在，如果不存在则创建
    folder.mkdir(parents=True, exist_ok=True)

    # 构建完整的文件路径：DATA_ROOT/username/NSFW级别/图片ID.扩展名
    path = folder / f"{img_id}.{ext}"

    tmp_path = path.with_suffix(path.suffix + ".part")
    # 如果文件已存在，跳过下载
    if path.exists():
        return True

    # 重试循环
    for attempt in range(max_retries):
        try:
            # 发送HTTP GET请求下载图片
            with requests.get(
                url,
                timeout=60,
                headers={"User-Agent": "Mozilla/5.0"},
                stream=True,
            ) as r:
                r.raise_for_status()

                with open(tmp_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            # 下载完成后原子替换
            tmp_path.replace(path)
            return True

        except requests.exceptions.ConnectionError as e:
            # 连接错误，重试
            if attempt < max_retries - 1:
                wait_time = REQUEST_DELAY * (attempt + 1)  # 递增等待时间
                print(f"[下载重试] {img_id} (尝试 {attempt + 1}/{max_retries}): {e}")
                time.sleep(wait_time)
            else:
                print(f"[下载失败] {img_id}: 连接被远程主机关闭 - {e}")

        except requests.exceptions.RequestException as e:
            # 网络 / HTTP 错误
            if attempt < max_retries - 1:
                wait_time = REQUEST_DELAY * (attempt + 1)
                print(f"[下载重试] {img_id} (尝试 {attempt + 1}/{max_retries}): {e}")
                time.sleep(wait_time)
            else:
                print(f"[下载失败] {img_id}: {e}")

        except Exception as e:
            # 文件系统 / 权限 / 其他异常
            print(f"[写入失败] {img_id}: {e}")
            break

    # 清理残留的临时文件
    if tmp_path.exists():
        tmp_path.unlink(missing_ok=True)

    return False


def download_all(username, need_list, progress_cb=None):
    """
    批量下载图片列表
    
    功能说明：
    - 使用多线程并发下载多个图片
    - 支持进度回调，实时反馈下载进度
    - 基于配置的最大工作线程数
    - 自动处理下载完成事件
    
    参数：
    username (str): 用户名，用于构建存储路径
    need_list (list): 需要下载的图片信息列表
    progress_cb (callable, optional): 进度回调函数，接收(done, total)参数
    """
    # 获取需要下载的图片总数
    total = len(need_list)
    # 已完成下载的数量
    done = 0

    # 创建线程池，最大线程数由配置文件定义
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        # 提交所有下载任务到线程池
        futures = [
            pool.submit(_download_one, username, info)
            for info in need_list
        ]

        # 遍历已完成的任务
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    done += 1
            except Exception:
                pass

            # 如果提供了进度回调，发送当前进度
            if progress_cb:
                progress_cb(done, total)
