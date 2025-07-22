import tkinter as tk
from tkinter import messagebox
import requests
import yaml
import math
import base64

# 設定ファイルからAPIキーを読み込み
def load_settings():
    try:
        with open('settings.ini', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config['api']['google_maps']['key']
    except FileNotFoundError:
        messagebox.showerror("エラー", "settings.iniファイルが見つかりません")
        return None
    except KeyError:
        messagebox.showerror("エラー", "settings.iniファイルの形式が正しくありません")
        return None
    except Exception as e:
        messagebox.showerror("エラー", f"設定ファイルの読み込みに失敗しました: {e}")
        return None

# APIキーを読み込み
API_KEY = load_settings()

def geocode_address(address):
    if not API_KEY:
        return None, None
    
    url = f"https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": API_KEY,
        "language": "ja"  # 日本語で結果を取得
    }
    response = requests.get(url, params=params).json()
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        return None, None

def calculate_distance(lat1, lng1, lat2, lng2):
    # ハーサイン距離計算
    R = 6371000  # 地球の半径（メートル）
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def find_nearest_station(lat, lng):
    if not API_KEY:
        return None
    
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": 3000,
        "type": "train_station",
        "key": API_KEY,
        "language": "ja"  # 日本語で駅名を取得
    }
    response = requests.get(url, params=params).json()
    if response["status"] == "OK" and response["results"]:
        stations = []
        for i in range(min(5, len(response["results"]))):
            station_info = response["results"][i]
            station_name = station_info["name"]
            station_lat = station_info["geometry"]["location"]["lat"]
            station_lng = station_info["geometry"]["location"]["lng"]

            # 直線距離
            distance_straight = calculate_distance(lat, lng, station_lat, station_lng)

            # Directions APIで道路距離を取得
            directions_url = "https://maps.googleapis.com/maps/api/directions/json"
            directions_params = {
                "origin": f"{lat},{lng}",
                "destination": f"{station_lat},{station_lng}",
                "mode": "walking",  # 徒歩ルート
                "key": API_KEY,
                "language": "ja"
            }
            directions_resp = requests.get(directions_url, params=directions_params).json()
            if directions_resp["status"] == "OK" and directions_resp["routes"]:
                distance_route = directions_resp["routes"][0]["legs"][0]["distance"]["value"]  # メートル単位
            else:
                distance_route = None

            stations.append({
                "name": station_name,
                "distance_straight": distance_straight,
                "distance_route": distance_route,
                "station_lat": station_lat,
                "station_lng": station_lng
            })
        return stations
    else:
        return None

# polylineデコード用関数
# Googleのエンコーディング仕様に従う
# 参考: https://developers.google.com/maps/documentation/utilities/polylinealgorithm

def decode_polyline(polyline_str):
    index, lat, lng, coordinates = 0, 0, 0, []
    while index < len(polyline_str):
        result, shift = 0, 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat
        result, shift = 0, 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng
        coordinates.append((lat / 1e5, lng / 1e5))
    return coordinates

# KMLファイル保存関数

def save_route_to_kml(coords, address_latlng, stations, filename="route.kml"):
    # 赤・太い・半透明（aabbggrr: 80%透明の赤=CC0000FF）
    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <Style id="redLineArrow">
    <LineStyle>
      <color>CC0000FF</color>
      <width>6</width>
    </LineStyle>
  </Style>
  <Style id="arrowIcon">
    <IconStyle>
      <scale>1.2</scale>
      <Icon>
        <href>http://maps.google.com/mapfiles/kml/shapes/arrow.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="pinAddress">
    <IconStyle>
      <color>ff00ff00</color>
      <scale>1.2</scale>
      <Icon>
        <href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="pinStation">
    <IconStyle>
      <color>ff0000ff</color>
      <scale>1.1</scale>
      <Icon>
        <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Placemark>
    <name>経路</name>
    <styleUrl>#redLineArrow</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
'''
    kml_footer = '''      </coordinates>
    </LineString>
  </Placemark>
'''
    # 住所ピン
    kml_address = f'''  <Placemark>
    <name>入力住所</name>
    <styleUrl>#pinAddress</styleUrl>
    <Point>
      <coordinates>{address_latlng[1]},{address_latlng[0]},0</coordinates>
    </Point>
  </Placemark>
'''
    # 駅ピン
    kml_stations = ""
    for i, st in enumerate(stations):
        kml_stations += f'''  <Placemark>
    <name>{st['name']}</name>
    <styleUrl>#pinStation</styleUrl>
    <Point>
      <coordinates>{st['station_lng']},{st['station_lat']},0</coordinates>
    </Point>
  </Placemark>
'''
    # 終点に矢印アイコン
    kml_arrow = f'''  <Placemark>
    <name>終点</name>
    <styleUrl>#arrowIcon</styleUrl>
    <Point>
      <coordinates>{coords[-1][1]},{coords[-1][0]},0</coordinates>
    </Point>
  </Placemark>
</Document>
</kml>'''
    coord_str = "\n".join([f"{lng},{lat},0" for lat, lng in coords])
    kml_content = kml_header + coord_str + "\n" + kml_footer + kml_address + kml_stations + kml_arrow
    with open(filename, "w", encoding="utf-8") as f:
        f.write(kml_content)

def search():
    if not API_KEY:
        result_label.config(text="APIキーが設定されていません")
        return
    
    address = entry.get()
    if not address:
        messagebox.showwarning("入力エラー", "住所を入力してください")
        return

    lat, lng = geocode_address(address)
    if lat is None:
        result_label.config(text="住所の取得に失敗しました")
        return

    stations = find_nearest_station(lat, lng)
    if stations:
        station_text = "最寄り駅:\n"
        # 最初の駅の道なり経路をKML保存
        first_station = stations[0]
        directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        directions_params = {
            "origin": f"{lat},{lng}",
            "destination": f"{first_station['station_lat']},{first_station['station_lng']}",
            "mode": "walking",
            "key": API_KEY,
            "language": "ja"
        }
        directions_resp = requests.get(directions_url, params=directions_params).json()
        if directions_resp["status"] == "OK" and directions_resp["routes"]:
            polyline = directions_resp["routes"][0]["overview_polyline"]["points"]
            coords = decode_polyline(polyline)
            save_route_to_kml(coords, (lat, lng), stations, filename="route.kml")
        # 駅リスト表示
        for i, station in enumerate(stations):
            straight = station['distance_straight']
            route = station['distance_route']
            straight_text = f"{straight}m" if straight < 1000 else f"{straight/1000:.1f}km"
            if route is not None:
                route_text = f"{route}m" if route < 1000 else f"{route/1000:.1f}km"
            else:
                route_text = "取得不可"
            station_text += f"{i+1}. {station['name']} (直線: {straight_text} / 道沿い: {route_text})\n"
        result_label.config(text=station_text)
    else:
        result_label.config(text="駅が見つかりませんでした")

# GUIセットアップ
root = tk.Tk()
root.title("最寄り駅検索アプリ")

tk.Label(root, text="住所を入力:").pack()
entry = tk.Entry(root, width=50)
entry.pack()

tk.Button(root, text="検索", command=search).pack(pady=10)

result_label = tk.Label(root, text="", fg="blue")
result_label.pack()

root.mainloop()