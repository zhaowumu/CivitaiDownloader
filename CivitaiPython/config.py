# -*- coding: utf-8 -*-
"""
Civitai 同步工具 - 配置管理模块
功能说明：
1. 提供配置文件的加载和管理功能
2. 支持从 config.ini 文件读取配置
3. 如果配置文件不存在，自动生成默认配置
4. 支持打包环境和开发环境的路径处理
5. 导出配置变量供其他模块使用

依赖模块：
- configparser: 用于配置文件的解析和生成
- os: 用于文件路径操作
- sys: 用于获取系统信息和运行时环境

作者: [作者名称]
创建日期: [创建日期]
版本: [版本号]
"""
# 以下是默认配置示例（已注释）
# 下载根目录
#DATA_ROOT = "CivitaiImageData"

# 下载线程数
#MAX_WORKERS = 8

# 请求间隔（防止封 IP）
#REQUEST_DELAY = 0.3

# 我的用户名
#MY_CIVITAI_NAME = "zhaowumu"

# API Key（如需要）
#CIVITAI_API_KEY = "48a2ee64f676a61c94169c95da2f81fc"

# 打包命令示例
#pyinstaller --noconfirm --onedir --windowed --name "CivitaiSyncTool" --add-data "core;core" --add-data "gui;gui" main.py

import configparser  # 用于配置文件的解析和生成
import os  # 用于文件路径操作
import sys  # 用于获取系统信息和运行时环境

# 关键：获取程序运行时的真实目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的环境 (.exe)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 如果是编辑器环境 (.py)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 确保 ini 文件是在 BASE_DIR 根目录下（而不是在 core 文件夹里）
# 如果你的 config.py 在 core/ 下，你需要根据结构调整，这里假设 config.py 在根目录
ini_path = os.path.join(BASE_DIR, 'config.ini')

# 创建配置解析器实例
config = configparser.ConfigParser()

# 检查配置文件是否存在
if not os.path.exists(ini_path):
    # 如果配置文件不存在，自动生成默认配置
    # 创建Common部分配置
    config['Common'] = {
        'data_root': 'CivitaiImageData',  # 下载根目录
        'max_workers': '8',  # 最大下载线程数
        'request_delay': '0.3',  # 请求间隔时间（秒）
        'allow_nsfw': 'True'  # 是否允许下载NSFW内容
    }
    # 创建User部分配置
    config['User'] = {
        'civitai_name': 'zhaowumu',  # 默认Civitai用户名
        'api_key': '48a2ee64f676a61c94169c95da2f81fc'  # 默认API密钥（示例）
    }
    # 写入配置文件
    with open(ini_path, 'w', encoding='utf-8') as f:
        config.write(f)
else:
    # 如果配置文件存在，读取配置
    config.read(ini_path, encoding='utf-8')

# 导出配置变量供其他模块使用
DATA_ROOT = config.get('Common', 'data_root', fallback='CivitaiImageData')  # 下载根目录
MAX_WORKERS = config.getint('Common', 'max_workers', fallback=8)  # 最大下载线程数
REQUEST_DELAY = config.getfloat('Common', 'request_delay', fallback=0.3)  # 请求间隔时间（秒）
ALLOW_NSFW = config.getboolean('Common', 'allow_nsfw', fallback=True)  # 是否允许下载NSFW内容
MY_CIVITAI_NAME = config.get('User', 'civitai_name', fallback='')  # 当前用户Civitai用户名
CIVITAI_API_KEY = config.get('User', 'api_key', fallback='')  # Civitai API密钥

# 调试打印（打包后可以在控制台看到，确认读取是否成功）
print(f"[CONFIG] Loading from: {ini_path}")
print(f"[CONFIG] Target User: {MY_CIVITAI_NAME}")