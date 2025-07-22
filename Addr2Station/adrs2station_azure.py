import requests

# あなたの Azure Maps API Key をここに設定してください
subscription_key = "keystring"  # ←ここを書き換えてください

# ジオコーディング対象の住所（例：東京都庁）
address = "東京都品川区"

def geocode_address(address):
    url = "https://atlas.microsoft.com/search/address/json"
    params = {
        "api-version": "1.0",
        "subscription-key": subscription_key,
        "query": address,
        "language": "ja"  # 日本語対応
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  # エラー時に例外を発生

    data = response.json()
    if not data["results"]:
        print("住所が見つかりませんでした。")
        return None

    position = data["results"][0]["position"]
    return position["lat"], position["lon"]

# 実行
latlon = geocode_address(address)
if latlon:
    lat, lon = latlon
    print(f"住所：{address}")
    print(f"緯度：{lat}, 経度：{lon}")
