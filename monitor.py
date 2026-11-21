import os
import time
import requests

COLLECTION_JSON_URL = "https://lovelive.fannect.jp/collections/ll-48-03/products.json"
PRODUCT_BASE_URL = "https://lovelive.fannect.jp/collections/ll-48-03/products/"

TARGET_KEYWORDS = [
    "蓮ノ空女学院校章ボタン風ピンズ",
]

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
CHECK_COUNT = 15   # 1회 실행당 15번 체크
INTERVAL_SEC = 60  # 1분(60초) 간격


def fetch_in_stock():
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(COLLECTION_JSON_URL, headers=headers, timeout=15)
    resp.raise_for_status()
    products = resp.json().get("products", [])

    found = {}
    for product in products:
        title = product.get("title", "")
        if any(keyword in title for keyword in TARGET_KEYWORDS):
            if any(v.get("available", False) for v in product.get("variants", [])):
                handle = product.get("handle", "")
                found[title] = f"{PRODUCT_BASE_URL}{handle}"
    return found


def main():
    alerted = set()

    for i in range(CHECK_COUNT):
        try:
            in_stock = fetch_in_stock()
            new_items = {k: v for k, v in in_stock.items() if k not in alerted}

            if new_items:
                lines = [f"- **{title}**\n  {url}" for title, url in new_items.items()]
                content = "@everyone 🚨 **하스노소라 핀즈 재입고 감지!**\n\n" + "\n".join(lines)
                requests.post(WEBHOOK_URL, json={"content": content}, timeout=10).raise_for_status()
                alerted.update(new_items.keys())
                print(f"[{i+1}/{CHECK_COUNT}] 재입고 알림 전송 완료:", list(new_items.keys()))
            else:
                print(f"[{i+1}/{CHECK_COUNT}] 품절 상태 (알림 없음)")
        except Exception as e:
            print(f"[{i+1}/{CHECK_COUNT}] 요청 오류 발생:", e)

        if i < CHECK_COUNT - 1:
            time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    main()
