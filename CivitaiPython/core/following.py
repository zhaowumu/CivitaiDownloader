import json
import requests

def get_all_following_usernames(username):
    """
    获取某个 Civitai 用户的所有关注用户名列表（自动剔除 username 为 none 的用户）
    """
    url = "https://civitai.com/api/trpc/user.getList"

    page = 1
    all_usernames = []

    while True:
        params = {
            "input": json.dumps({
                "json": {
                    "username": username,
                    "type": "following",
                    "page": page,
                    "limit": 50,
                    "authed": True
                }
            })
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        result = data.get("result", {}).get("data", {}).get("json", {})
        items = result.get("items", [])

        if not items:
            break

        # 关键修改：过滤掉 username 为 none / None / 空字符串
        all_usernames.extend(
            u["username"]
            for u in items
            if u.get("username") not in (None, "", "none")
        )

        current_page = result.get("currentPage", page)
        total_pages = result.get("totalPages", page)

        print(f"更新用户：{current_page}/{total_pages}")

        if current_page >= total_pages:
            break

        page += 1

    print(f"更新用户：{len(all_usernames)}")
    return all_usernames
