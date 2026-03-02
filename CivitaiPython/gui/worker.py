# -*- coding: utf-8 -*-
"""
Civitai 同步工具 - 后台工作线程
功能说明：
1. 继承自QThread，用于在后台线程中执行同步和下载任务
2. 与UI线程通过信号槽机制通信，避免UI阻塞
3. 支持多种工作模式：JSON同步、图片下载、全部同步
4. 提供详细的任务状态和进度反馈

依赖模块：
- PyQt5.QtCore: 提供QThread和pyqtSignal类
- core.sync: 提供CivitaiSyncManager核心同步管理类
- traceback: 用于异常信息格式化

作者: [作者名称]
创建日期: [创建日期]
版本: [版本号]
"""
from PyQt5.QtCore import QThread, pyqtSignal
from core.sync import CivitaiSyncManager  # 导入核心同步管理类
import traceback  # 用于异常信息格式化


class SyncWorker(QThread):
    """
    同步工作线程类
    功能说明：
    - 在后台线程中执行Civitai用户的同步和下载任务
    - 通过信号槽机制与UI线程通信，提供进度和状态反馈
    - 支持三种工作模式：JSON同步、图片下载、全部同步
    """
    # 定义信号
    log = pyqtSignal(str)  # 日志信号，传递日志消息
    finished = pyqtSignal()  # 任务完成信号
    error = pyqtSignal(str)  # 错误信号，传递异常信息
    progress = pyqtSignal(int, int)  # 进度信号，传递(已完成, 总数)
    stats = pyqtSignal(int, int, int)  # 统计信号，传递(远程数, 本地数, 需要下载数)

    # 新增: 同步 JSON 时的数量变化信号
    json_count_update = pyqtSignal(int)  # JSON同步进度信号，传递当前获取的记录数
    # 新增: 同步 JSON 时的当前页面URL状态信号
    current_page_update = pyqtSignal(str)  # 传递当前处理的页面URL
    # 新增: 日志信号
    log_msg = pyqtSignal(str)  # 传递日志消息
    data_updated = pyqtSignal()  # 数据更新完成信号

    def __init__(self, username, mode="all"):
        """
        初始化同步工作线程
        参数：
        - username: 要同步的Civitai用户名
        - mode: 工作模式，可选值："json"(仅同步JSON)、"download"(仅下载图片)、"all"(全部同步)
        """
        super().__init__()
        self.username = username  # 保存用户名
        self.mode = mode  # 保存工作模式

    def run(self):
        """
        线程运行方法
        功能说明：
        - 创建CivitaiSyncManager实例
        - 根据工作模式执行相应的同步或下载任务
        - 处理任务进度和状态反馈
        - 捕获并处理异常
        """
        try:
            # 发送任务开始日志
            self.log.emit(f"[{self.username}] 任务开始: {self.mode}")

            # 定义进度回调函数
            def on_progress(done, total):
                self.progress.emit(done, total)

            # 定义统计回调函数
            def on_stats(remote, local, need):
                self.stats.emit(remote, local, need)

            # 定义JSON同步进度回调函数
            def on_json_progress(count):
                self.json_count_update.emit(count)

            # 定义当前页面URL回调函数
            def on_page_update(url):
                self.current_page_update.emit(url)

            # 定义日志回调函数
            def on_log(msg):
                self.log_msg.emit(msg)

            # 创建CivitaiSyncManager实例
            manager = CivitaiSyncManager(
                self.username,
                on_progress=on_progress,  # 进度回调
                on_stats=on_stats,  # 统计回调
                on_json_progress=on_json_progress,  # JSON同步进度回调
                on_page_update=on_page_update,  # 当前页面URL回调
                on_log=on_log  # 日志回调
            )

            # 根据工作模式执行相应任务
            if self.mode == "json":
                manager.sync_json()  # 仅同步JSON数据
                self.log.emit(f"[{self.username}] JSON 更新完毕")

            elif self.mode == "download":
                manager.sync_download()  # 仅下载缺失的图片
                self.log.emit(f"[{self.username}] 下载完毕")

            else:  # all
                manager.sync_all()  # 同步JSON并下载图片
                self.log.emit(f"[{self.username}] 全部同步完毕")

            # 发送数据更新完成信号
            self.data_updated.emit()
            # 发送任务完成信号
            self.finished.emit()

        except Exception:
            # 捕获并发送异常信息
            self.error.emit(traceback.format_exc())