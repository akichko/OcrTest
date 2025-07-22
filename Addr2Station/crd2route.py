import requests
from azure_param import subscription_key

# Azure Maps APIキー
#subscription_key = "YOUR_AZURE_MAPS_PRIMARY_KEY"  # ←ここを書き換えてください

# 出発地点（新宿駅）
start_lat, start_lon = 35.690921, 139.700257

# 到着地点（東京駅）
end_lat, end_lon = 35.681236, 139.767125

def save_route_to_kml(points, filename="route.kml"):
    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <Style id="routeLine">
    <LineStyle>
      <color>CC0000FF</color> <!-- 半透明赤 -->
      <width>5</width>
    </LineStyle>
  </Style>
  <Placemark>
    <name>ルート</name>
    <styleUrl>#routeLine</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
'''
    kml_footer = '''      </coordinates>
    </LineString>
  </Placemark>
</Document>
</kml>'''
    coord_str = "\n".join([f"{pt['longitude']},{pt['latitude']},0" for pt in points])
    kml_content = kml_header + coord_str + "\n" + kml_footer
    with open(filename, "w", encoding="utf-8") as f:
        f.write(kml_content)

def calculate_route(start_lat, start_lon, end_lat, end_lon):
    url = "https://atlas.microsoft.com/route/directions/json"

    params = {
        "api-version": "1.0",
        "subscription-key": subscription_key,
        "query": f"{start_lat},{start_lon}:{end_lat},{end_lon}",
        "travelMode": "car",  # または "walk", "bicycle", "truck"
        "language": "ja-JP",
        "routeType": "fastest",
        "traffic": "true"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    summary = data["routes"][0]["summary"]
    instructions = data["routes"][0]["legs"][0]["points"]

    print("✅ ルート情報:")
    print(f"- 距離: {summary['lengthInMeters'] / 1000:.2f} km")
    print(f"- 所要時間: {summary['travelTimeInSeconds'] // 60} 分")

    # ルート全体の座標（折れ線などに使える）
    print("\n🗺️ 経路の主要なポイント:")
    for idx, pt in enumerate(instructions[::max(1, len(instructions)//5)], 1):
        print(f"{idx}. 緯度: {pt['latitude']}, 経度: {pt['longitude']}")

    # KML保存
    save_route_to_kml(instructions, filename="route.kml")

# 実行
calculate_route(start_lat, start_lon, end_lat, end_lon)
