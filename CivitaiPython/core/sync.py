import time
import requests
from config import REQUEST_DELAY
from contextlib import contextmanager
from core.storage import save_json, load_json, load_cursor, save_cursor
from core.diff import get_need_download
from core.downloader import download_all

# Civitai API基础URL
BASE_URL = "https://civitai.com/api/v1/images"


@contextmanager
def create_session():
    """
    创建并管理requests会话的上下文管理器
    确保会话在使用后正确关闭，避免资源泄漏
    """
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    try:
        yield session
    finally:
        session.close()


class CivitaiSyncManager:
    """
    Civitai用户数据同步管理器
    
    功能说明：
    - 管理Civitai用户数据的同步和下载流程
    - 支持仅同步JSON数据、仅执行下载和全流程同步
    - 实现了断点续传功能
    - 提供进度回调机制，方便UI展示
    - 自动处理数据合并和重复检测
    """

    def __init__(self, username, on_progress=None, on_stats=None, on_json_progress=None, on_page_update=None, on_log=None):
        """
        初始化同步管理器
        
        参数：
        username (str): 要同步的Civitai用户名
        on_progress (callable, optional): 下载进度回调函数
        on_stats (callable, optional): 统计信息回调函数
        on_json_progress (callable, optional): JSON数据同步进度回调函数
        on_page_update (callable, optional): 当前页面URL状态回调函数
        on_log (callable, optional): 日志消息回调函数
        """
        self.username = username  # 要同步的用户名
        self.on_progress = on_progress  # 下载进度回调
        self.on_stats = on_stats  # 统计信息回调
        self.on_json_progress = on_json_progress  # JSON同步进度回调
        self.on_page_update = on_page_update  # 当前页面URL回调
        self.on_log = on_log  # 日志回调

    def _log(self, message):
        """
        发送日志消息到回调函数，并输出到终端
        参数：
        - message: 日志消息内容
        """
        print(message)  # 同时输出到终端
        if self.on_log:
            self.on_log(message)

    def json_extract_fields(self, item):
        """
        从原始item中提取精简后的字段
        仅保留后续下载与展示所需的核心字段
        """
        return {
            "id": item.get("id"),
            "url": item.get("url"),
            "nsfwLevel": item.get("nsfwLevel"),
            "type": item.get("type"),
            "nsfw": item.get("nsfw"),
            "createdAt": item.get("createdAt"),      # 若后续无需meta可再删减
        }

    def sync_json(self, max_retries=3, timeout=300):
        """
        仅同步JSON数据
        
        功能说明：
        - 从Civitai API获取最新的图片数据
        - 支持增量保存，每获取一页就保存一次，避免中断时数据丢失
        - 加载本地已有的图片数据
        - 合并新旧数据，去重并保留最新信息
        - 保存合并后的数据和同步进度
        - 支持自动重试机制，避免网络波动导致获取失败
        - 添加总超时限制，避免长时间卡住
        
        参数：
        max_retries (int): 最大重试次数，默认3次
        timeout (int): 总超时时间（秒），默认300秒（5分钟）
        
        返回：
        dict: 合并后的图片数据字典
        """
        # 加载上次同步的进度游标
        start_url = load_cursor(self.username)

        # 加载本地已有的图片数据
        merged = load_json(self.username)

        self._log(f"[同步] 加载已经存在json数据数量: {len(merged)}")

        # 精简本地已有数据，仅保留后续需要的核心字段
        merged = {k: self.json_extract_fields(v) for k, v in merged.items()}

        # 使用上下文管理器创建会话，确保资源正确释放
        with create_session() as session:
            # 确定初始请求URL
            if start_url:
                url = start_url
            else:
                url = (
                    f"{BASE_URL}"
                    f"?username={self.username}"
                    f"&limit=20"
                    f"&nsfw=X"
                    f"&period=AllTime"
                    f"&sort=Oldest"
                    f"&cursor=0|1500000000000"
                )

            self._log(f"[同步] 开始同步游标: {url}")

            last_url = None
            total_images = len(merged)
            start_time = time.time()  # 记录开始时间

            # 循环获取所有分页数据
            while url:
                # 检查是否超时
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    self._log(f"[同步] 超时（{elapsed:.0f}秒），保存当前进度")
                    save_cursor(self.username, url)
                    save_json(self.username, merged)
                    return merged

                # 在请求之前先发送当前URL状态
                if self.on_page_update:
                    self.on_page_update(url)
                
                retry_count = 0
                success = False
                
                # 尝试获取当前页，支持重试
                while retry_count < max_retries and not success:
                    try:
                        #print(f"[FETCH] json page {url}")
                        # 发送GET请求，设置30秒超时
                        resp = session.get(url, timeout=30)
                        # 检查响应状态码，如果不是200则抛出异常
                        resp.raise_for_status()
                        success = True
                    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                        retry_count += 1
                        if retry_count < max_retries:
                            wait_time = REQUEST_DELAY * retry_count
                            self._log(f"[重试] 获取JSON页面失败 (尝试 {retry_count}/{max_retries}): {e}")
                            # 重试时也更新UI显示
                            if self.on_page_update:
                                self.on_page_update(f"[重试 {retry_count}/{max_retries}] {url}")
                            time.sleep(wait_time)
                        else:
                            self._log(f"[同步] 获取JSON页面失败，保存当前进度: {e}")
                            save_cursor(self.username, url)
                            save_json(self.username, merged)
                            return merged

                # 解析JSON响应数据
                data = resp.json()
                # 获取当前页的图片列表
                items = data.get("items", [])

                # 将当前页的图片提取精简字段后转换为字典并合并到已有数据中
                page_dict = {i["id"]: self.json_extract_fields(i) for i in items}
                merged.update(page_dict)

                # 保存当前进度（增量保存，避免中断时数据丢失）
                save_cursor(self.username, url)
                save_json(self.username, merged)

                # 更新已获取的图片总数
                total_images += len(items)

                # 触发页面获取完成回调
                if self.on_json_progress:
                    self.on_json_progress(total_images)

                # 获取分页元数据，准备处理下一页
                meta = data.get("metadata", {})

                # 获取下一页的URL
                next_url = meta.get("nextPage")
                last_url = next_url
                self._log(f"[同步] json next page {next_url}")

                # 如果没有下一页，退出循环
                if not next_url:
                    break

                # 更新URL为下一页地址
                url = next_url
                # 等待指定的延迟时间，避免触发API速率限制
                time.sleep(REQUEST_DELAY)

        self._log(f"[同步] 合并后的json数据数量: {len(merged)}")
        # 返回合并后的数据
        return merged

    def sync_download(self):
        """
        仅执行下载（基于现有JSON）
        
        功能说明：
        - 基于本地已有的JSON数据
        - 检查哪些图片需要下载
        - 执行下载操作
        - 提供下载进度反馈
        """

        # 加载本地已有的图片数据
        merged = load_json(self.username)
        # 检查哪些图片需要下载（本地不存在的文件）
        need = get_need_download(self.username, merged)

        self._log(f"[下载] 需要下载的数据数量: {len(need)}")

        # 如果提供了统计回调，发送统计信息
        if self.on_stats:
            self.on_stats(len(merged), 0, len(need))

        # 执行下载操作
        download_all(
            self.username,
            need,  # 需要下载的图片列表
            progress_cb=self.on_progress  # 下载进度回调
        )

    def sync_all(self):
        """
        全流程同步
        
        功能说明：
        - 先执行JSON数据同步
        - 然后执行下载操作
        - 提供完整的进度反馈
        """
        # 先同步JSON数据
        merged = self.sync_json()
        # 检查哪些图片需要下载
        need = get_need_download(self.username, merged)

        # 如果提供了统计回调，发送统计信息
        if self.on_stats:
            self.on_stats(len(merged), 0, len(need))

        # 执行下载操作
        download_all(
            self.username,
            need,  # 需要下载的图片列表
            progress_cb=self.on_progress  # 下载进度回调
        )
