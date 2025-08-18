import os
import requests
import json

# Variables d'entorn (cal definir-les al teu .env o al sistema)
RENDER_API_KEY = os.getenv("RENDER_API_KEY")
SERVICE_ID = os.getenv("RENDER_SERVICE_ID")  # Exemple: "srv-xxxxxx"

# Validem que estiguin definides
if not RENDER_API_KEY or not SERVICE_ID:
    raise ValueError("Falten variables d'entorn: RENDER_API_KEY o RENDER_SERVICE_ID")

# Payload de la petició
payload = {
    "serviceId": SERVICE_ID,
    "branch": "main",
    "rootDirectory": "",
    "clearCache": True
}

# Headers amb l'API Key
headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Content-Type": "application/json"
}

# Endpoint de Render per iniciar el deploy
url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"

try:
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("[RENDER] Deploy OK:", json.dumps(response.json(), indent=2))
    else:
        print("[RENDER] Deploy Fallit:", response.status_code, response.text)
except requests.exceptions.RequestException as e:
    print("[RENDER] Error de connexió:", str(e))
