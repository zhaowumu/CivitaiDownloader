# -*- coding: utf-8 -*-
"""
Civitai 高级同步工具 - GUI 主界面
功能说明：
1. 提供用户友好的图形界面，用于管理Civitai用户的关注、同步和下载操作
2. 支持单个用户和批量用户的JSON同步与图片下载
3. 实现了队列管理和后台任务处理，避免UI阻塞
4. 提供进度显示和状态反馈
5. 支持打开用户本地文件夹功能

依赖模块：
- PyQt5: 用于构建GUI界面
- core模块: 提供核心业务逻辑（同步、下载、存储等）
- config: 提供配置信息（如MY_CIVITAI_NAME）

作者: [作者名称]
创建日期: [创建日期]
版本: [版本号]
"""
import os
import sys
import platform
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QProgressBar, QScrollArea, QFrame, QMessageBox,
    QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal

from gui.worker import SyncWorker      # 导入同步工作线程类
from core.following import get_all_following_usernames  # 获取关注用户列表
from core.storage import user_dir, list_local_users, get_user_stats, load_cursor  # 存储相关功能
from config import MY_CIVITAI_NAME    # 配置的Civitai用户名


class UserWidget(QFrame):
    """
    单个用户的 UI 卡片组件
    功能说明：
    - 显示单个Civitai用户的信息卡片
    - 提供同步JSON、下载图片、打开文件夹等操作按钮
    - 显示用户的JSON数量和已下载数量统计
    - 支持任务状态显示和进度条
    """
    # 自定义信号定义
    req_sync_json = pyqtSignal(str)      # 请求同步JSON的信号，传递用户名
    req_download = pyqtSignal(str)       # 请求下载图片的信号，传递用户名
    req_open_folder = pyqtSignal(str)    # 请求打开文件夹的信号，传递用户名

    def __init__(self, username, index=0, parent=None):
        """
        初始化用户卡片组件
        参数：
        - username: 用户名
        - index: 用户在列表中的索引，用于实现斑马纹背景
        - parent: 父窗口组件
        """
        super().__init__(parent)
        self.username = username  # 保存用户名
        self.setFrameShape(QFrame.StyledPanel)  # 设置边框样式

        # 视觉分割：增加交替背景色（斑马纹），提高可读性
        bg_color = "#ffffff" if index % 2 == 0 else "#f4f4f4"
        self.setStyleSheet(f"UserWidget {{ background-color: {bg_color}; border-bottom: 1px solid #ddd; }}")
        self.setFixedHeight(115)  # 增加高度，确保新添加的游标标签能正确显示

        # 主布局：水平布局
        main_layout = QHBoxLayout(self)
        
        # 左侧信息布局：垂直布局，显示用户信息
        info_layout = QVBoxLayout()

        # 用户名标签：粗体显示
        self.lbl_name = QLabel(f"<b>{username}</b>")
        self.lbl_name.setStyleSheet("font-size: 14px; background: transparent;")

        # 统计信息标签：显示JSON数量和已下载数量
        self.lbl_stats = QLabel("读取中...")
        self.lbl_stats.setStyleSheet("color: #666; background: transparent;")

        # 状态标签：显示当前状态（就绪、正在同步等）
        self.lbl_status = QLabel("就绪")
        self.lbl_status.setStyleSheet("color: #005fb8; font-size: 11px; font-weight: bold; background: transparent;")

        # 游标URL标签：显示同步进度游标
        self.lbl_cursor = QLabel("游标: 无")
        self.lbl_cursor.setStyleSheet("color: #666; font-size: 11px; background: transparent;")
        self.lbl_cursor.setWordWrap(True)  # 自动换行

        # 将标签添加到信息布局
        info_layout.addWidget(self.lbl_name)
        info_layout.addWidget(self.lbl_stats)
        info_layout.addWidget(self.lbl_status)
        info_layout.addWidget(self.lbl_cursor)
        info_layout.addStretch()  # 添加弹性空间，使内容顶部对齐

        # 进度条：用于显示下载进度，默认隐藏
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)  # 显示进度百分比文本
        self.progress.setRange(0, 100)  # 默认范围0-100
        self.progress.setValue(0)  # 默认值0
        self.progress.setFixedWidth(200)  # 固定宽度
        self.progress.hide()  # 初始隐藏

        # 右侧按钮布局：垂直布局，包含操作按钮
        btn_layout = QVBoxLayout()
        top_btn_layout = QHBoxLayout()  # 顶部按钮布局（水平）
        
        # 同步JSON按钮
        self.btn_json = QPushButton("同步Json")
        # 只下载按钮
        self.btn_dl = QPushButton("只下载")
        
        top_btn_layout.addWidget(self.btn_json)
        top_btn_layout.addWidget(self.btn_dl)

        # 打开文件夹按钮
        self.btn_folder = QPushButton("打开文件夹")
        
        btn_layout.addLayout(top_btn_layout)  # 添加顶部按钮布局
        btn_layout.addWidget(self.btn_folder)  # 添加打开文件夹按钮

        # 将各个布局添加到主布局
        main_layout.addLayout(info_layout, stretch=1)  # 信息布局占据主要空间
        main_layout.addWidget(self.progress)  # 添加进度条
        main_layout.addLayout(btn_layout)  # 添加按钮布局

        # 连接按钮点击信号到相应的处理函数
        self.btn_json.clicked.connect(lambda: self.req_sync_json.emit(self.username))
        self.btn_dl.clicked.connect(lambda: self.req_download.emit(self.username))
        self.btn_folder.clicked.connect(lambda: self.req_open_folder.emit(self.username))

        self.refresh_stats()  # 刷新统计信息

    def refresh_stats(self):
        """
        刷新用户的JSON数量、已下载文件数量和游标URL
        功能说明：
        - 调用core.storage中的get_user_stats函数获取统计数据
        - 获取并显示当前的同步进度游标URL
        - 更新相应标签的显示内容
        - 处理可能的异常情况
        """
        try:
            # 获取统计数据：JSON记录数和已下载文件数
            j_count, f_count = get_user_stats(self.username)
            self.lbl_stats.setText(f"Json: {j_count} | 已下载: {f_count}")

            # 获取并显示游标URL
            cursor_url = load_cursor(self.username)
            if cursor_url:
                # 不再限制显示长度，允许自动换行显示完整URL
                self.lbl_cursor.setText(f"游标: {cursor_url}")
            else:
                self.lbl_cursor.setText("游标: 无")
        except Exception as e:
            # 发生异常时显示错误信息
            self.lbl_stats.setText("统计失败")
            self.lbl_cursor.setText("游标: 获取失败")

    def set_running(self, is_running, mode_text=""):
        """
        设置组件的运行状态
        参数：
        - is_running: 是否正在运行任务
        - mode_text: 运行模式文本（如"json"、"download"）
        功能说明：
        - 根据运行状态启用/禁用按钮
        - 更新状态标签的显示内容
        - 根据模式决定是否显示进度条
        """
        # 根据运行状态启用/禁用操作按钮
        self.btn_json.setEnabled(not is_running)
        self.btn_dl.setEnabled(not is_running)

        if is_running:
            # 运行中状态：更新状态文本
            self.lbl_status.setText(f"正在{mode_text}...")
            # 如果是下载模式，显示并重置进度条
            if mode_text == "download":
                self.progress.show()
                self.progress.setValue(0)
        else:
            # 非运行状态：隐藏进度条，重置状态文本
            self.progress.hide()
            self.lbl_status.setText("就绪")

    def update_json_count(self, count):
        """
        更新同步JSON时的记录数量显示
        参数：
        - count: 当前已获取的JSON记录数
        """
        self.lbl_status.setText(f"正在获取: {count} 条记录...")

    def update_progress(self, done, total):
        """
        更新下载进度显示
        参数：
        - done: 已完成的下载数量
        - total: 总下载数量
        功能说明：
        - 更新进度条的最大值和当前值
        - 更新状态标签显示当前进度
        """
        self.progress.setMaximum(total)  # 设置进度条最大值
        self.progress.setValue(done)     # 设置进度条当前值
        self.lbl_status.setText(f"进度: {done}/{total}")  # 更新状态文本


class MainWindow(QWidget):
    """
    Civitai高级同步工具的主窗口
    功能说明：
    - 提供应用的主要界面布局和控制功能
    - 管理用户列表和用户卡片组件
    - 处理同步和下载任务的队列管理
    - 协调后台工作线程与UI组件的交互
    """
    def __init__(self):
        """
        初始化主窗口
        功能说明：
        - 设置窗口标题和尺寸
        - 创建界面布局（顶部控制栏、中间滚动列表、底部日志条）
        - 初始化状态管理变量
        - 加载本地用户列表
        """
        super().__init__()
        self.setWindowTitle("Civitai 高级同步工具")  # 设置窗口标题
        self.resize(950, 750)  # 设置窗口尺寸

        # 核心布局：垂直布局
        layout = QVBoxLayout()

        # --- 顶部控制栏 --- 包含主要操作按钮
        top_layout = QHBoxLayout()

        # 刷新列表按钮：重新加载本地用户列表
        self.btn_refresh_list = QPushButton("刷新列表")
        self.btn_refresh_list.clicked.connect(self.load_user_list)

        # 获取关注列表按钮：通过API获取用户的关注列表
        self.btn_fetch_follow = QPushButton("获取关注列表(API)")
        self.btn_fetch_follow.clicked.connect(self.fetch_following_users)

        # 一键同步所有JSON按钮：批量同步所有用户的JSON数据
        self.btn_sync_all_json = QPushButton("一键同步所有JSON")
        self.btn_sync_all_json.clicked.connect(self.batch_sync_json)

        # 一键下载所有缺失按钮：批量下载所有用户的缺失图片
        self.btn_download_all = QPushButton("一键下载所有缺失")
        self.btn_download_all.clicked.connect(self.batch_download)

        # 添加按钮到顶部布局
        top_layout.addWidget(self.btn_refresh_list)
        top_layout.addWidget(self.btn_fetch_follow)
        top_layout.addStretch()  # 添加弹性空间，将按钮分组
        top_layout.addWidget(self.btn_sync_all_json)
        top_layout.addWidget(self.btn_download_all)

        layout.addLayout(top_layout)  # 将顶部布局添加到主布局

        # --- 中间滚动列表区域 --- 用于显示用户卡片
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)  # 设置滚动区域可调整大小

        # 创建容器组件用于存放用户卡片
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        # 设置布局属性：无边距、无间距、顶部对齐
        self.container_layout.setSpacing(0)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.container)  # 将容器设置为滚动区域的内容
        layout.addWidget(self.scroll)  # 将滚动区域添加到主布局

        # --- 底部日志条 --- 显示全局状态信息
        self.lbl_global_status = QLabel("Ready.")
        layout.addWidget(self.lbl_global_status)

        self.setLayout(layout)  # 设置窗口的主布局

        # 状态管理变量
        self.user_widgets = {}  # 存储所有用户卡片组件，键为用户名
        self.workers = {}  # 存储当前运行的工作线程，键为用户名
        self.queue = []  # 任务队列，存储待处理的任务 (用户名, 模式)
        self.is_processing_queue = False  # 队列是否正在处理中

        self.load_user_list()  # 初始化时加载本地用户列表

    # ==========================
    # 核心业务逻辑
    # ==========================
    def load_user_list(self):
        """
        扫描本地目录并加载用户卡片
        功能说明：
        - 清空现有的用户卡片和容器布局
        - 调用list_local_users获取本地用户列表
        - 为每个用户创建并添加UserWidget组件
        - 更新全局状态信息
        """
        # 清空现有用户卡片：从后往前删除，避免索引问题
        for i in reversed(range(self.container_layout.count())):
            w = self.container_layout.itemAt(i).widget()
            if w: w.deleteLater()  # 安全删除组件

        self.user_widgets.clear()  # 清空用户组件字典

        # 获取本地存储的用户列表
        users = list_local_users()
        # 为每个用户创建并添加UserWidget
        for idx, u in enumerate(users):
            self.add_user_widget(u, idx)

        # 更新全局状态文本
        self.lbl_global_status.setText(f"加载了 {len(users)} 个用户")

    def add_user_widget(self, username, index=0):
        """
        添加单个用户卡片到界面
        参数：
        - username: 用户名
        - index: 用户在列表中的索引，用于实现斑马纹背景
        功能说明：
        - 检查用户是否已存在，避免重复添加
        - 创建UserWidget实例并设置信号连接
        - 将组件添加到容器布局并保存到字典
        """
        # 检查用户是否已存在于组件字典中
        if username in self.user_widgets:
            return

        # 创建UserWidget实例
        w = UserWidget(username, index)
        # 连接用户组件的信号到相应的处理函数
        w.req_sync_json.connect(self.handle_sync_json)
        w.req_download.connect(self.handle_download)
        w.req_open_folder.connect(self.handle_open_folder)

        self.container_layout.addWidget(w)  # 将组件添加到容器布局
        self.user_widgets[username] = w  # 将组件保存到字典中

    def fetch_following_users(self):
        """
        通过API获取关注的用户列表
        功能说明：
        - 调用core.following中的get_all_following_usernames函数
        - 为每个关注的用户创建本地目录
        - 刷新用户列表显示
        - 处理成功和失败情况并显示消息框
        """
        # 更新全局状态文本
        self.lbl_global_status.setText("正在通过 API 获取关注列表...")
        QApplication.processEvents()  # 强制刷新UI显示，确保用户看到状态更新

        try:
            # 获取当前用户关注的所有用户名
            names = get_all_following_usernames(MY_CIVITAI_NAME)
            new_count = 0
            for n in names:
                # user_dir函数内部会自动创建用户目录
                path = user_dir(n)
                # 简单判断是否是新创建的用户
                # （如果之前没有data.json文件且没有子目录，可视为新用户）
                # 这里为了简单直接根据names刷新列表

            # 刷新用户列表显示
            self.load_user_list()
            # 显示成功消息框
            QMessageBox.information(self, "完成", f"已同步关注列表。\n当前总计关注用户: {len(names)}")
        except Exception as e:
            # 显示错误消息框
            QMessageBox.critical(self, "错误", f"获取失败: {str(e)}")

        # 恢复默认状态文本
        self.lbl_global_status.setText("Ready.")

    def handle_open_folder(self, username):
        """
        打开用户本地文件夹
        参数：
        - username: 用户名
        功能说明：
        - 根据操作系统类型选择合适的方式打开文件夹
        - 支持Windows、macOS和Linux系统
        """
        # 获取用户目录的绝对路径
        path = str(user_dir(username).absolute())
        # 根据不同操作系统选择打开文件夹的方式
        if platform.system() == "Windows":
            os.startfile(path)  # Windows使用os.startfile
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])  # macOS使用open命令
        else:
            subprocess.Popen(["xdg-open", path])  # Linux使用xdg-open命令

    def handle_sync_json(self, username):
        """
        处理同步JSON请求
        参数：
        - username: 用户名
        """
        self.start_worker(username, "json")

    def handle_download(self, username):
        """
        处理下载请求
        参数：
        - username: 用户名
        """
        self.start_worker(username, "download")

    # ==========================
    # 队列与批量处理
    # ==========================
    def batch_sync_json(self):
        """
        批量同步所有用户的JSON数据
        功能说明：
        - 获取所有本地用户列表
        - 将每个用户的JSON同步任务添加到队列
        - 启动队列处理
        """
        # 获取所有本地用户
        users = list_local_users()
        # 将每个用户的JSON同步任务添加到队列
        for u in users:
            self.queue.append((u, "json"))
        # 开始处理队列
        self.process_queue()

    def batch_download(self):
        """
        批量下载所有用户的缺失图片
        功能说明：
        - 获取所有本地用户列表
        - 将每个用户的下载任务添加到队列
        - 启动队列处理
        """
        # 获取所有本地用户
        users = list_local_users()
        # 将每个用户的下载任务添加到队列
        for u in users:
            self.queue.append((u, "download"))
        # 开始处理队列
        self.process_queue()

    def process_queue(self):
        """
        处理任务队列
        功能说明：
        - 检查队列是否正在处理或为空
        - 从队列头部取出任务
        - 确保对应的用户卡片可见
        - 启动工作线程处理任务
        """
        # 如果队列正在处理，直接返回
        if self.is_processing_queue:
            return

        # 如果队列为空，更新状态并返回
        if not self.queue:
            self.lbl_global_status.setText("批量任务完成")
            return

        # 设置队列正在处理的标志
        self.is_processing_queue = True
        # 从队列头部取出任务
        username, mode = self.queue.pop(0)

        # 如果用户卡片存在，确保其在滚动区域可见
        if username in self.user_widgets:
            self.scroll.ensureWidgetVisible(self.user_widgets[username])

        # 启动工作线程处理任务
        self.start_worker(username, mode, is_queue=True)

    def start_worker(self, username, mode, is_queue=False):
        """
        启动后台工作线程
        参数：
        - username: 用户名
        - mode: 工作模式 ("json" 或 "download")
        - is_queue: 是否来自队列
        功能说明：
        - 检查用户是否已有工作线程在运行
        - 设置用户卡片为运行状态
        - 创建SyncWorker实例并连接信号
        - 启动工作线程
        """
        # 如果用户已有工作线程在运行，根据是否来自队列决定后续操作
        if username in self.workers:
            if is_queue:
                # 如果来自队列，标记队列未在处理并继续处理下一个任务
                self.is_processing_queue = False
                self.process_queue()
            return

        # 如果用户卡片存在，设置其为运行状态
        if username in self.user_widgets:
            self.user_widgets[username].set_running(True, mode)

        # 创建SyncWorker实例
        worker = SyncWorker(username, mode)
        # 连接工作线程的日志信号到全局状态标签
        worker.log.connect(lambda msg: self.lbl_global_status.setText(f"[{username}] {msg}"))

        # 如果用户卡片存在，连接工作线程的进度信号
        if username in self.user_widgets:
            w = self.user_widgets[username]
            worker.progress.connect(w.update_progress)  # 进度更新信号
            worker.json_count_update.connect(w.update_json_count)  # JSON数量更新信号
            worker.data_updated.connect(w.refresh_stats)  # 数据更新后刷新统计信号

        # 连接工作线程完成信号
        worker.finished.connect(lambda: self.on_worker_finished(username, is_queue))
        # 连接工作线程错误信号（仅打印到控制台）
        worker.error.connect(lambda err: print(f"Error {username}: {err}"))

        # 保存工作线程引用
        self.workers[username] = worker
        # 启动工作线程
        worker.start()

    def on_worker_finished(self, username, is_queue):
        """
        处理工作线程完成事件
        参数：
        - username: 用户名
        - is_queue: 是否来自队列
        功能说明：
        - 清理工作线程引用
        - 重置用户卡片的运行状态
        - 刷新用户统计信息
        - 如果来自队列，继续处理下一个任务
        """
        # 清理工作线程引用
        if username in self.workers:
            del self.workers[username]

        # 重置用户卡片状态
        if username in self.user_widgets:
            self.user_widgets[username].set_running(False)
            self.user_widgets[username].refresh_stats()  # 刷新统计信息

        # 如果来自队列，继续处理下一个任务
        if is_queue:
            self.is_processing_queue = False
            self.process_queue()