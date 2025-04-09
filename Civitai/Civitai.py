import json
import ssl
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import shutil
from urllib.parse import urlparse

import aiohttp
import asyncio

import certifi
import requests
from aiohttp.resolver import AsyncResolver

class App:
    def __init__(self, root):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.user_images_dir = os.path.join(self.base_dir, "UserImages")

        # 初始化用户目录
        self.ensure_directory_exists(self.user_images_dir)

        self.root = root
        self.root.title("用户图像管理器")
        self.create_widgets()
        self.populate_list()

    def ensure_directory_exists(self, path):
        """确保目录存在，不存在则创建"""
        if not os.path.exists(path):
            os.makedirs(path)

    def create_widgets(self):
        # 创建顶部按钮框架
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)

        # 创建操作按钮
        ttk.Button(btn_frame, text="添加项目", command=self.show_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除选中", command=self.delete_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空所有", command=self.clear_all).pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="同步数据", command=self.FetchUserData).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="异步下载", command=self.DownloadUserData).pack(side=tk.LEFT, padx=10)

        # 创建主内容框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建左侧列表框框架
        left_frame = ttk.Frame(main_frame, padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建右侧列表框框架
        right_frame = ttk.Frame(main_frame, padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 创建左侧列表框
        self.folder_list = tk.Listbox(left_frame, width=30, height=20)
        self.folder_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5)

        # 添加滚动条
        left_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.folder_list.yview)
        self.folder_list.configure(yscrollcommand=left_scrollbar.set)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建右侧列表框
        self.file_list = tk.Listbox(right_frame, width=30, height=20)
        self.file_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5)

        # 添加滚动条
        right_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=right_scrollbar.set)
        right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定事件
        self.folder_list.bind("<ButtonRelease-1>", self.update_file_list)
        self.file_list.bind("<ButtonRelease-1>", self.update_status)

        # 初始化列表
        self.populate_list()

    def populate_list(self):
        """从文件系统加载目录列表"""
        self.folder_list.delete(0, tk.END)
        try:
            folders = [f for f in os.listdir(self.user_images_dir)
                       if os.path.isdir(os.path.join(self.user_images_dir, f))]
            for folder in sorted(folders):
                self.folder_list.insert(tk.END, folder)
        except Exception as e:
            messagebox.showerror("错误", f"读取目录失败: {str(e)}")

    def show_input(self):
        """显示输入对话框"""
        new_item = simpledialog.askstring(
            "添加项目",
            "请输入新项目名称:",
            parent=self.root
        )
        if new_item:
            self.add_folder(new_item)

    def add_folder(self, folder_name):
        """创建文件夹并更新列表"""
        target_path = os.path.join(self.user_images_dir, folder_name)

        if os.path.exists(target_path):
            messagebox.showwarning("警告", "该文件夹已存在")
            return

        try:
            os.mkdir(target_path)
            self.folder_list.insert(tk.END, folder_name)
            #messagebox.showinfo("成功", "文件夹创建成功")
        except Exception as e:
            messagebox.showerror("错误", f"创建文件夹失败: {str(e)}")

    def delete_item(self):
        """删除选中项及其文件夹"""
        selected = self.folder_list.curselection()
        if not selected:
            return

        item = self.folder_list.get(selected[0])
        folder_path = os.path.join(self.user_images_dir, item)

        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                self.folder_list.delete(selected[0])
                self.file_list.delete(0, tk.END)
                self.status_bar.config(text="就绪")
                messagebox.showinfo("成功", "文件夹已删除")
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {str(e)}")
        else:
            self.folder_list.delete(selected[0])

    def clear_all(self):
        """清空所有文件夹"""
        for item in self.folder_list.get(0, tk.END):
            folder_path = os.path.join(self.user_images_dir, item)
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)
                except Exception as e:
                    messagebox.showerror("错误", f"删除 {item} 失败: {str(e)}")

        self.folder_list.delete(0, tk.END)
        self.file_list.delete(0, tk.END)
        self.status_bar.config(text="就绪")

    def FetchUserData(self):

        """显示当前选中的用户名"""
        selected = self.folder_list.curselection()
        if selected:
            user = self.folder_list.get(selected[0])
            self.RequestUserData(user)

        else:
            messagebox.showwarning("警告", "请先选择一个用户")

    def RequestUserData(self,userName):


        VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.mpg', '.mpeg', '.3gp', '.webm','.jpeg','.jpg','.bmp','.png')

        page = 3
        try:
            params = {
                "token": "48a2ee64f676a61c94169c95da2f81fc",
                "username": userName,
                "nsfw": "X",
                "limit":200,
                "page": 15,
                "sort":"Newest"
            }

            response = requests.get(
                "https://civitai.com/api/v1/images",
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            if "items" not in data or not isinstance(data["items"], list):
                raise ValueError("无效的响应数据结构")



            download_list = []
            for idx, item in enumerate(data["items"], 1):
                url = item.get('url', '')
                idNum = item.get('id', '')
                if url.lower().endswith(VIDEO_EXTENSIONS):
                    print(f"{idNum}-{url}")  # 输出: example.com-123
                    download_list.append({"id": idNum, "url": url})


            target_path = os.path.join(self.user_images_dir, userName)
            jsonPath = os.path.join(target_path, "data.json")
            print("当前下载列表数量为：", len(download_list))
            messagebox.showwarning("数量", f"当前下载列表数量为：{len(download_list)}")
            # 写入 JSON 文件（覆盖模式）
            with open(jsonPath, "w", encoding="utf-8") as f:
                json.dump(download_list, f, ensure_ascii=False, indent=4)  # 美化输出，支持中文

        except PermissionError:
            messagebox.showerror("错误", "无权限写入系统根目录！")

        except Exception as e:
            messagebox.showerror("错误", f"获取数据失败: {str(e)}")

        finally:
            print(f"JSON 文件已保存")

    def SyncDownloadUserData(self):
        print("同步下载")
        """同步下载实现"""
        selected = self.folder_list.curselection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个用户")
            return

        user = self.folder_list.get(selected[0])
        target_dir = os.path.join(self.user_images_dir, user)
        json_path = os.path.join(target_dir, "data.json")

        # 检查数据文件存在性
        if not os.path.exists(json_path):
            messagebox.showerror("错误", "未找到数据文件")
            return

        try:
            # 读取下载列表
            with open(json_path, "r", encoding="utf-8") as f:
                download_list = json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"读取数据失败: {str(e)}")
            return

        # 获取本地已下载文件集合
        local_files = {f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))}

        # 显示进度状态
        self.status_bar.config(text=f"开始同步下载 {user} 的文件...")
        self.root.update_idletasks()

        # 顺序下载处理
        for item in download_list:
            url = item.get('url', '')
            file_id = item.get('id', '')
            if not url or not file_id:
                continue

            # 解析文件信息
            parsed_url = urlparse(url)
            ext = os.path.splitext(parsed_url.path)[1].lower()
            if not ext:
                continue

            target_file = f"{file_id}{ext}"
            if target_file in local_files:
                continue

            file_path = os.path.join(target_dir, target_file)
            try:
                # 同步下载实现
                with requests.get(url, verify=certifi.where(), stream=True, timeout=30) as response:
                    response.raise_for_status()
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                # 更新进度显示
                self.file_list.insert(tk.END, target_file)
                self.status_bar.config(text=f"完成下载: {target_file}")
                self.root.update_idletasks()
            except Exception as e:
                self.status_bar.config(text=f"下载失败: {url}")
                self.root.update_idletasks()
                print(f"同步下载失败 {url}: {str(e)}")

        messagebox.showinfo("完成", f"{user} 的同步下载任务结束")





    def DownloadUserData(self):
        selected = self.folder_list.curselection()
        if selected:
            print("开始异步下载")
            user = self.folder_list.get(selected[0])
            target_dir = os.path.join(self.user_images_dir, user)
            json_path = os.path.join(target_dir, "data.json")
            if not os.path.exists(json_path):
                messagebox.showerror("错误", "未找到数据文件")
                return

            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    download_list = json.load(f)
            except Exception as e:
                messagebox.showerror("错误", f"读取数据失败: {str(e)}")
                return

            # 获取本地已下载文件集合
            local_files = set()
            for f in os.listdir(target_dir):
                file_path = os.path.join(target_dir, f)
                if os.path.isfile(file_path):
                    local_files.add(f)

            # 准备下载队列
            download_queue = []
            for item in download_list:
                url = item.get('url', '')
                file_id = item.get('id', '')
                if not url or not file_id:
                    continue

                # 提取扩展名
                parsed_url = urlparse(url)
                ext = os.path.splitext(parsed_url.path)[1].lower()
                if not ext:
                    continue

                # 生成目标文件名
                target_file = f"{file_id}{ext}"
                if target_file not in local_files:
                    download_queue.append({
                        'url': url,
                        'target': os.path.join(target_dir, target_file),
                        'id': file_id
                    })
                    print(target_file)


            if not download_queue:
                messagebox.showinfo("提示", "所有文件已下载完成")
                return

            asyncio.run(self.process_json(download_queue, target_dir))


        else:
            messagebox.showwarning("警告", "请先选择一个用户")


    """异步下载单个文件并生成智能文件名"""
    async def download_file(self,session, url, file_path, semaphore):
        """异步下载单个文件并保存"""
        print(file_path)
        response = requests.get(url)
        with open("video.mp4", "wb") as f:
            f.write(response.content)

        try:
            # 同步下载实现
            with requests.get(url, verify=certifi.where(), stream=True, timeout=30) as response:
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            # 更新进度显示
            self.file_list.insert(tk.END, file_path)
            self.status_bar.config(text=f"完成下载: {file_path}")
            self.root.update_idletasks()
        except Exception as e:
            self.status_bar.config(text=f"下载失败: {url}")
            self.root.update_idletasks()
            print(f"异步下载失败 {url}: {str(e)}")

    async def process_json(self,json_data, save_dir):

        print("process_json")
        # 并发控制
        semaphore = asyncio.Semaphore(1)
        """处理JSON数据并启动下载任务"""
        timeout = aiohttp.ClientTimeout(
            total=60,
            connect=30,
            sock_read=60
        )
        # 配置SSL和DNS
        ssl_context = ssl.create_default_context()

        connector = aiohttp.TCPConnector(
            ssl=ssl_context,
            limit=100,
            limit_per_host=50
        )
        # 解析JSON数据
        async with aiohttp.ClientSession(connector=connector,timeout=timeout) as session:
            tasks = []
            for item in json_data:
                # 提取文件名和扩展名
                parsed_url = urlparse(item['url'])
                file_ext = os.path.splitext(parsed_url.path)[1]  # 提取扩展名（如.jpg）
                file_name = f"{item['id']}{file_ext}"
                file_path = os.path.join(save_dir, file_name)  # 正确拼接方式

                # 创建下载任务
                task = asyncio.create_task(self.download_file(session, item['url'], file_path, semaphore))
                tasks.append(task)

            # 并发执行所有任务
            await asyncio.gather(*tasks)

    def update_file_list(self, event):
        """更新右侧文件列表"""
        # 获取鼠标点击位置的项索引
        clicked_index = self.folder_list.nearest(event.y)
        selected_folder = self.folder_list.curselection()
        if clicked_index in selected_folder:

            if not selected_folder:
                self.file_list.delete(0, tk.END)
                self.status_bar.config(text="未选择文件夹")
                return

            folder_name = self.folder_list.get(selected_folder)
            folder_path = os.path.join(self.user_images_dir, folder_name)

            self.file_list.delete(0, tk.END)
            try:
                files = [f for f in os.listdir(folder_path)
                         if os.path.isfile(os.path.join(folder_path, f))]
                for file in sorted(files):
                    self.file_list.insert(tk.END, file)
                self.status_bar.config(text=f"已选择: {folder_name} ({len(files)} 个文件)")
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败: {str(e)}")
                self.status_bar.config(text="读取文件失败")

    def update_status(self, event):
        """更新状态栏显示"""
        selected = self.file_list.curselection()
        if selected:
            file_name = self.file_list.get(selected[0])
            self.status_bar.config(text=f"已选择文件: {file_name}")
        else:
            self.status_bar.config(text="就绪")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.geometry("800x600")
    root.mainloop()