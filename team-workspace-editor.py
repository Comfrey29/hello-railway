from flask import Flask, request, jsonify
import os
import subprocess
import threading
import shutil

app = Flask(__name__)

BOTS_DIR = "bots"
BOTS_PROCESSES = {}

if not os.path.exists(BOTS_DIR):
    os.makedirs(BOTS_DIR)

def run_bot(bot_id, script_file):
    bot_script_path = os.path.join(BOTS_DIR, bot_id, script_file)
    proc = subprocess.Popen(['python', bot_script_path])
    BOTS_PROCESSES[bot_id] = proc
    proc.wait()
    if bot_id in BOTS_PROCESSES:
        del BOTS_PROCESSES[bot_id]

@app.route('/bots', methods=['GET'])
def list_bots():
    bots = os.listdir(BOTS_DIR)
    return jsonify(bots)

@app.route('/bots/upload', methods=['POST'])
def upload_bot():
    bot_id = request.form.get('bot_id')
    file = request.files.get('file')

    if not bot_id or not file:
        return jsonify({'error': 'Missing bot_id or file'}), 400

    bot_path = os.path.join(BOTS_DIR, bot_id)
    os.makedirs(bot_path, exist_ok=True)
    filepath = os.path.join(bot_path, file.filename)
    file.save(filepath)
    return jsonify({'message': f'Bot {bot_id} uploaded successfully'})

@app.route('/bots/start/<bot_id>', methods=['POST'])
def start_bot(bot_id):
    if bot_id in BOTS_PROCESSES:
        return jsonify({'message': f'Bot {bot_id} is already running'}), 400

    bot_path = os.path.join(BOTS_DIR, bot_id)
    scripts = [f for f in os.listdir(bot_path) if f.endswith('.py')]
    if not scripts:
        return jsonify({'error': 'No script found for bot'}), 404

    script = scripts[0]
    t = threading.Thread(target=run_bot, args=(bot_id, script), daemon=True)
    t.start()
    return jsonify({'message': f'Bot {bot_id} started'})

@app.route('/bots/stop/<bot_id>', methods=['POST'])
def stop_bot(bot_id):
    proc = BOTS_PROCESSES.get(bot_id)
    if not proc:
        return jsonify({'message': f'Bot {bot_id} is not running'}), 400
    proc.terminate()
    proc.wait(timeout=5)
    del BOTS_PROCESSES[bot_id]
    return jsonify({'message': f'Bot {bot_id} stopped'})

@app.route('/bots/delete/<bot_id>', methods=['DELETE'])
def delete_bot(bot_id):
    if bot_id in BOTS_PROCESSES:
        proc = BOTS_PROCESSES[bot_id]
        proc.terminate()
        proc.wait(timeout=5)
        del BOTS_PROCESSES[bot_id]
    shutil.rmtree(os.path.join(BOTS_DIR, bot_id), ignore_errors=True)
    return jsonify({'message': f'Bot {bot_id} deleted'})

@app.route('/bots/info/<bot_id>', methods=['GET'])
def bot_info(bot_id):
    bot_path = os.path.join(BOTS_DIR, bot_id)
    scripts = [f for f in os.listdir(bot_path) if f.endswith('.py')]
    running = bot_id in BOTS_PROCESSES
    return jsonify({
        'bot_id': bot_id,
        'scripts': scripts,
        'running': running
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
