import json
import requests
import urllib.parse
from config import CIVITAI_API_KEY


def get_all_following_usernames(username):
    """
    终极修复版：处理 404/400 错误，适配 2025 tRPC Batch 协议
    """
    # 路径必须精确，不能多斜杠或少斜杠
    endpoint = "https://civitai.com/api/trpc/user.getList"

    page = 1
    all_usernames = []

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": f"https://civitai.com/user/{username}/following",
        "x-trpc-source": "react",
    }

    if CIVITAI_API_KEY:
        headers["Authorization"] = f"Bearer {CIVITAI_API_KEY}"

    session.headers.update(headers)

    while True:
        # 1. 构造标准的 tRPC 输入对象
        inner_query = {
            "username": username,
            "type": "following",
            "page": page,
            "limit": 50
        }

        # 2. 关键修复：tRPC Batch 模式要求 input 是一个键为 "0" 的对象
        # 格式为: {"0": {"json": {...}}}
        payload = {
            "0": {
                "json": inner_query
            }
        }

        # 3. 将对象转为紧凑的 JSON 字符串并进行 URL 编码
        input_str = json.dumps(payload, separators=(',', ':'))
        encoded_input = urllib.parse.quote(input_str)

        # 4. 构造完整带 batch=1 的 URL
        # 这是目前最不容易报 404 的格式
        full_url = f"{endpoint}?batch=1&input={encoded_input}"

        print(f"[FETCH] Page {page}...")

        try:
            response = session.get(full_url, timeout=20)

            if response.status_code != 200:
                print(f"DEBUG URL: {full_url}")
                print(f"DEBUG RESPONSE: {response.text}")
                response.raise_for_status()

            data = response.json()

            # 5. 解析数组格式的返回结果
            # Batch 模式返回的是 [{ "result": { "data": { "json": { "items": [...] } } } }]
            if isinstance(data, list) and len(data) > 0:
                res_obj = data[0]
            else:
                res_obj = data

            # 逐层安全获取数据
            result_data = res_obj.get("result", {}).get("data", {}).get("json", {})
            items = result_data.get("items", [])

            if not items:
                break

            for it in items:
                u_name = it.get("username")
                if u_name:
                    all_usernames.append(u_name)

            # 分页判断
            total_pages = result_data.get("totalPages", 1)
            print(f"进度: {page}/{total_pages}")

            if page >= total_pages:
                break

            page += 1

        except Exception as e:
            print(f"API 请求失败: {e}")
            raise e

    # 去重并排序
    final_list = sorted(list(set(all_usernames)))
    print(f"成功获取 {len(final_list)} 个关注用户")
    return final_list