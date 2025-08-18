import requests
import json

RENDER_API_KEY = "rnd_ZPNdatMLFOP31mkFQ1ubAmzzRVsq"
API_URL = "https://api.render.com/v1/services"

with open("data.json") as f:
    data = json.load(f)

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Content-Type": "application/json",
}

response = requests.post(API_URL, headers=headers, json=data)
print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")
