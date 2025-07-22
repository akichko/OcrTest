import requests
from azure_param import subscription_key
#subscription_key = "YOUR_AZURE_MAPS_KEY"
lat = 35.6895
lon = 139.6917
radius = 1000

url = "https://atlas.microsoft.com/search/nearby/json"
params = {
    "api-version": "1.0",
    "subscription-key": subscription_key,
    "lat": lat,
    "lon": lon,
    "radius": radius,
    "categorySet": "7380004,7380005",  # 駅
    "limit": 10,
    "language": "ja-JP"
}

response = requests.get(url, params=params)
response.raise_for_status()

results = response.json().get("results", [])

for idx, poi in enumerate(results, start=1):
    name = poi["poi"]["name"]
    addr = poi["address"]["freeformAddress"]
    dist = poi["dist"]
    print(f"{idx}. {name}（{addr}）- 距離: {int(dist)}m")
