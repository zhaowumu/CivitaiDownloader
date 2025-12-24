import time
import requests
from config import REQUEST_DELAY

BASE_URL = "https://civitai.com/api/v1/images"


def fetch_user_images(username, start_url=None, limit=20, on_page_fetched=None):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })

    images = []

    if start_url:
        url = start_url
    else:
        url = (
            f"{BASE_URL}"
            f"?username={username}"
            f"&limit={limit}"
            f"&nsfw=X"
            f"&period=AllTime"
            f"&sort=Oldest"
        )

    while url:
        print(f"[FETCH] page {url}")
        resp = session.get(url, timeout=30)
        resp.raise_for_status()

        data = resp.json()
        items = data.get("items", [])
        meta = data.get("metadata", {})

        images.extend(items)

        # 触发回调，通知当前抓取到的总数
        if on_page_fetched:
            on_page_fetched(len(images))

        next_url = meta.get("nextPage")

        # 注意：如果我们要继续合并，last_url 应该记录最后一个有数据的 nextPage 或者是当前 url
        # 这里为了 cursor 逻辑，保留 last_url 为 meta.get("nextPage") 逻辑
        if not next_url:
            break

        url = next_url
        time.sleep(REQUEST_DELAY)

    # 返回收集到的列表和最后一个有效分页地址
    return images, url