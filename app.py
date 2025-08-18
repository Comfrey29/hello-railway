from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "API is running"

@app.route('/callback')
def callback():
    # Implementació de callback si es vol
    return "Callback endpoint"

@app.route('/validate_token', methods=['POST'])
def validate_token():
    data = request.get_json()
    token = data.get('token')
    if not token:
        return jsonify({'valid': False, 'error': 'No token provided'}), 400
    headers = {'Authorization': f'Bot {token}'}
    r = requests.get('https://discord.com/api/v10/users/@me', headers=headers)
    if r.status_code == 200:
        return jsonify({'valid': True})
    else:
        return jsonify({'valid': False, 'error': 'Invalid token'}), 401

@app.route('/health', methods=['GET'])
def health():
    # Aquest endpoint indica que el servei està viu i saludable
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

