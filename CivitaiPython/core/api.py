import time
import requests
from config import REQUEST_DELAY
from contextlib import contextmanager

# Civitai API基础URL
BASE_URL = "https://civitai.com/api/v1/images"


@contextmanager
def create_session():
    """
    创建并管理requests会话的上下文管理器
    确保会话在使用后正确关闭，避免资源泄漏
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })
    try:
        yield session
    finally:
        session.close()


def fetch_user_images(username, start_url=None, limit=20, on_page_fetched=None, max_retries=3):
    """
    从Civitai API获取指定用户的所有图片
    
    功能说明：
    - 通过Civitai v1 API分页获取用户上传的图片
    - 支持自定义起始URL、分页大小和页面获取回调
    - 实现了请求延迟控制，避免触发API速率限制
    - 自动处理分页，直到获取完所有图片
    - 支持自动重试机制，避免网络波动导致获取失败
    - 返回完整的图片列表和最后一个分页地址（用于断点续传）
    
    参数：
    username (str): 要查询的Civitai用户名
    start_url (str, optional): 起始分页URL，用于断点续传，默认None
    limit (int, optional): 每页获取的图片数量，默认20
    on_page_fetched (callable, optional): 页面获取完成后的回调函数，接收当前已获取总数作为参数
    max_retries (int): 最大重试次数，默认3次
    
    返回：
    tuple: (images, last_url)
        - images: 图片数据列表，包含完整的图片元数据
        - last_url: 最后一个有效分页地址，用于断点续传
    """
    # 使用上下文管理器创建会话，确保资源正确释放
    with create_session() as session:
        # 存储所有获取到的图片数据
        images = []

        # 确定初始请求URL
        if start_url:
            # 如果提供了起始URL，使用该URL开始获取
            url = start_url
        else:
            # 否则，构造初始请求URL
            url = (
                f"{BASE_URL}"
                f"?username={username}"  # 指定用户名
                f"&limit={limit}"        # 每页图片数量
                f"&nsfw=X"              # 包含所有NSFW级别内容
                f"&period=AllTime"      # 时间范围：所有时间
                f"&sort=Oldest"         # 排序方式：最旧的优先
            )

        # 循环获取所有分页数据
        while url:
            retry_count = 0
            success = False
            
            # 尝试获取当前页，支持重试
            while retry_count < max_retries and not success:
                try:
                    print(f"[FETCH] page {url}")
                    # 发送GET请求，设置30秒超时
                    resp = session.get(url, timeout=30)
                    # 检查响应状态码，如果不是200则抛出异常
                    resp.raise_for_status()
                    success = True
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = REQUEST_DELAY * retry_count
                        print(f"[重试] 获取页面失败 (尝试 {retry_count}/{max_retries}): {e}")
                        time.sleep(wait_time)
                    else:
                        print(f"[获取失败] 跳过页面 {url}: {e}")
                        break
            
            if not success:
                break

            # 解析JSON响应数据
            data = resp.json()
            # 获取当前页的图片列表
            items = data.get("items", [])
            # 获取分页元数据
            meta = data.get("metadata", {})

            # 将当前页的图片添加到总列表中
            images.extend(items)

            # 触发页面获取完成回调，如果提供了回调函数
            if on_page_fetched:
                on_page_fetched(len(images))  # 传入当前已获取的图片总数

            # 获取下一页的URL
            next_url = meta.get("nextPage")

            # 注意：如果我们要继续合并，last_url应该记录最后一个有数据的nextPage或者是当前url
            # 这里为了cursor逻辑，保留last_url为meta.get("nextPage")逻辑
            if not next_url:
                # 如果没有下一页，退出循环
                break

            # 更新URL为下一页地址
            url = next_url
            # 等待指定的延迟时间，避免触发API速率限制
            time.sleep(REQUEST_DELAY)

    # 返回收集到的图片列表和最后一个有效分页地址
    return images, url
