import tkinter as tk
from tkinter import messagebox
import requests
import yaml
import math

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

def find_nearest_station(lat, lng):
    if not API_KEY:
        return None
    
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": 1000,
        "type": "train_station",
        "key": API_KEY,
        "language": "ja"  # 日本語で駅名を取得
    }
    response = requests.get(url, params=params).json()
    if response["status"] == "OK" and response["results"]:
        # 最大3つの駅を返す（駅名と距離を含む）
        stations = []
        for i in range(min(3, len(response["results"]))):
            station_info = response["results"][i]
            station_name = station_info["name"]
            
            # 距離を計算（緯度経度から直線距離を計算）
            station_lat = station_info["geometry"]["location"]["lat"]
            station_lng = station_info["geometry"]["location"]["lng"]
            distance = calculate_distance(lat, lng, station_lat, station_lng)
            
            stations.append({
                "name": station_name,
                "distance": distance
            })
        return stations
    else:
        return None

def calculate_distance(lat1, lng1, lat2, lng2):
    """2点間の直線距離を計算（メートル単位）"""
    # 地球の半径（メートル）
    R = 6371000
    
    # 緯度経度をラジアンに変換
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # 緯度経度の差
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    # ハバーサイン公式で距離を計算
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return round(distance)

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
        for i, station in enumerate(stations):
            distance_text = f"{station['distance']}m" if station['distance'] < 1000 else f"{station['distance']/1000:.1f}km"
            station_text += f"{i+1}. {station['name']} ({distance_text})\n"
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