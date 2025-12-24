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

#打包命令
#pyinstaller --noconfirm --onedir --windowed --name "CivitaiSyncTool" --add-data "core;core" --add-data "gui;gui" main.py

import configparser
import os
import sys

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

config = configparser.ConfigParser()

if not os.path.exists(ini_path):
    # 自动生成默认配置
    config['Common'] = {
        'data_root': 'CivitaiImageData',
        'max_workers': '8',
        'request_delay': '0.3',
        'allow_nsfw': 'True'
    }
    config['User'] = {
        'civitai_name': 'zhaowumu',
        'api_key': '48a2ee64f676a61c94169c95da2f81fc'
    }
    with open(ini_path, 'w', encoding='utf-8') as f:
        config.write(f)
else:
    config.read(ini_path, encoding='utf-8')

# 导出变量
DATA_ROOT = config.get('Common', 'data_root', fallback='CivitaiImageData')
MAX_WORKERS = config.getint('Common', 'max_workers', fallback=8)
REQUEST_DELAY = config.getfloat('Common', 'request_delay', fallback=0.3)
ALLOW_NSFW = config.getboolean('Common', 'allow_nsfw', fallback=True)
MY_CIVITAI_NAME = config.get('User', 'civitai_name', fallback='')
CIVITAI_API_KEY = config.get('User', 'api_key', fallback='')

# 调试打印（打包后可以在控制台看到，确认读取是否成功）
print(f"[CONFIG] Loading from: {ini_path}")
print(f"[CONFIG] Target User: {MY_CIVITAI_NAME}")