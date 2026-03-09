import json
import requests
import urllib.parse
from config import CIVITAI_API_KEY


def get_all_following_usernames(username):
    """
    获取指定Civitai用户的所有关注用户列表
    
    功能说明：
    - 通过Civitai的tRPC API批量获取用户关注列表
    - 支持分页加载，自动处理所有页面
    - 实现了tRPC Batch协议适配，解决404/400错误问题
    - 包含完整的错误处理和调试信息
    - 返回去重并排序后的关注用户名列表
    
    参数：
    username (str): 要查询的Civitai用户名
    
    返回：
    list[str]: 关注用户的用户名列表
    """
    # API端点URL，必须精确匹配tRPC端点路径
    endpoint = "https://civitai.com/api/trpc/user.getList"

    # 初始化分页参数
    page = 1  # 从第一页开始
    all_usernames = []  # 存储所有获取到的用户名

    # 创建会话对象，优化网络请求性能
    session = requests.Session()
    
    # 构建请求头，模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",  # 接收JSON格式响应
        "Referer": f"https://civitai.com/user/{username}/following",  # 模拟从用户关注页面发起请求
        "x-trpc-source": "react",  # 标识请求来源为React前端
    }

    # 如果配置了API密钥，则添加认证头
    if CIVITAI_API_KEY:
        headers["Authorization"] = f"Bearer {CIVITAI_API_KEY}"

    # 将请求头应用到会话
    session.headers.update(headers)

    # 循环获取所有分页数据
    while True:
        # 1. 构造tRPC API的查询参数
        inner_query = {
            "username": username,  # 目标用户名
            "type": "following",  # 获取关注列表类型
            "page": page,  # 当前页码
            "limit": 50  # 每页获取50条记录
        }

        # 2. 关键修复：适配tRPC Batch模式要求
        # tRPC Batch协议要求input必须是键为"0"的对象，格式为{"0": {"json": {...}}}
        payload = {
            "0": {
                "json": inner_query
            }
        }

        # 3. 将请求负载转换为紧凑JSON字符串并进行URL编码
        input_str = json.dumps(payload, separators=(',', ':'))  # 使用紧凑格式减少字符数
        # 使用quote进行URL编码，避免urlencode产生的input=前缀
        encoded_input = urllib.parse.quote(input_str, safe='')

        # 4. 构造完整的请求URL
        # 添加batch=1参数标识这是一个批量请求
        full_url = f"{endpoint}?batch=1&input={encoded_input}"

        # 打印当前获取进度
        print(f"[FETCH] Page {page}...")

        try:
            # 发送GET请求，设置20秒超时
            response = session.get(full_url, timeout=20)

            # 检查响应状态码
            if response.status_code != 200:
                print(f"DEBUG URL: {full_url}")  # 打印调试URL
                print(f"DEBUG RESPONSE: {response.text}")  # 打印调试响应内容
                response.raise_for_status()  # 抛出HTTP错误异常

            # 解析JSON响应
            data = response.json()

            # 5. 处理tRPC Batch响应格式
            # Batch模式返回的是数组格式：[{ "result": { "data": { "json": { "items": [...] } } } }]
            if isinstance(data, list) and len(data) > 0:
                res_obj = data[0]  # 获取第一个(也是唯一的)响应对象
            else:
                res_obj = data  # 兼容非数组格式的响应

            # 逐层安全获取数据，避免KeyError
            result_data = res_obj.get("result", {}).get("data", {}).get("json", {})
            items = result_data.get("items", [])  # 获取用户列表

            # 如果没有更多数据，退出循环
            if not items:
                break

            # 提取用户名并添加到结果列表
            for it in items:
                u_name = it.get("username")  # 安全获取用户名
                if u_name:  # 确保用户名不为空
                    all_usernames.append(u_name)

            # 计算分页进度
            total_pages = result_data.get("totalPages", 1)  # 总页数，默认为1
            print(f"进度: {page}/{total_pages}")

            # 检查是否已获取所有页面
            if page >= total_pages:
                break

            # 进入下一页
            page += 1

        except Exception as e:
            # 捕获并打印所有异常
            print(f"API请求失败: {e}")
            raise e  # 重新抛出异常，让调用者处理

    # 去重并排序最终结果
    final_list = sorted(list(set(all_usernames)))
    print(f"成功获取 {len(final_list)} 个关注用户")
    return final_list