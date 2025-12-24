import requests
import json
from config import MY_CIVITAI_NAME


def get_following_list(username, page=1, limit=50):
    """
    获取Civitai用户的关注列表

    Args:
        username: 用户名
        page: 页码（从1开始）
        limit: 每页数量
    """
    url = "https://civitai.com/api/trpc/user.getList"

    params = {
        "input": json.dumps({
            "json": {
                "username": username,
                "type": "following",
                "page": page,
                "limit": limit,
                "authed": True
            }
        })
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        # 解析响应数据
        data = response.json()

        # 提取用户数据
        # print(data)
        result = data.get("result", {}).get("data", {}).get("json", {})
        # print(result)
        users = result.get("items", [])
        # print(users)
        metadata = result.get("metadata", {})
        print(metadata)

        return {
            "users": users,
            "metadata": metadata,
            "total": metadata.get("total", 0),
            "current_page": metadata.get("currentPage", page),
            "page_size": metadata.get("pageSize", limit)
        }

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None


# 使用示例
if __name__ == "__main__":

    result = get_following_list(MY_CIVITAI_NAME, page=1, limit=50)

    if result:
        print(f"总关注数: {result['total']}")
        print(f"当前页: {result['current_page']}")
        print(f"用户数量: {len(result['users'])}")

        # 打印前几个用户信息
        for i, user in enumerate(result['users'][:], 1):
            print(f"{i}. 用户名: {user.get('username')} | ID: {user.get('id')}")

