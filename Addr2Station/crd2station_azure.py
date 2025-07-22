import requests

# Azure Maps の Primary Key を設定
subscription_key = "apikey"  # ←ここを自分のキーに置き換え

# 入力：検索の中心となる緯度・経度と半径（メートル）
latitude = 35.6895     # 例：新宿あたりの緯度
longitude = 139.6917   # 例：新宿あたりの経度
radius_m = 1000        # 半径1km

def search_stations_nearby(lat, lon, radius):
    url = "https://atlas.microsoft.com/search/poi/category/json"
    params = {
        "api-version": "1.0",
        "subscription-key": subscription_key,
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "limit": 10,              # 表示する駅の数
        "categorySet": "7332",    # 駅（Train Station）のカテゴリコード
        "language": "ja-JP",
        "query": "駅"  # ←追加
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    if not results:
        print("周辺に駅が見つかりませんでした。")
        return

    print(f"\n[半径 {radius}m 内の駅一覧]")
    for idx, station in enumerate(results, start=1):
        name = station["poi"]["name"]
        address = station["address"]["freeformAddress"]
        dist = station.get("dist", "不明")
        print(f"{idx}. {name}（{address}） - 距離: {int(dist)}m")

# 実行
search_stations_nearby(latitude, longitude, radius_m)
