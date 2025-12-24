import time
import requests
from config import REQUEST_DELAY

BASE_URL = "https://civitai.com/api/v1/images"


def fetch_user_images(username, start_url=None, limit=20):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })

    images = []
    last_url = None

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
        last_url = url
        url = meta.get("nextPage")

        if url:
            time.sleep(REQUEST_DELAY)

    return images, last_url
