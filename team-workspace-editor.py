import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import shutil
from flask import Flask, request, jsonify
import logging
from threading import Thread

BOTS_DIR = "bots"
BOTS_PROCESSES = {}

# Crear directori si no existeix
os.makedirs(BOTS_DIR, exist_ok=True)

# ------------------------- Funcions de gestió de bots -------------------------

def listar_bots():
    try:
        return os.listdir(BOTS_DIR)
    except Exception:
        return []

def pujar_bot(listbox):
    bot_id = simpledialog.askstring("Nom del bot", "Introdueix un identificador pel bot:")
    if not bot_id:
        return
    file_path = filedialog.askopenfilename(title="Tria fitxer .py del bot", filetypes=[("Arxius Python", "*.py")])
    if not file_path:
        return
    bot_path = os.path.join(BOTS_DIR, bot_id)
    os.makedirs(bot_path, exist_ok=True)
    dst_path = os.path.join(bot_path, os.path.basename(file_path))
    try:
        shutil.copyfile(file_path, dst_path)
        if bot_id not in listbox.get(0, tk.END):
            listbox.insert(tk.END, bot_id)
        messagebox.showinfo("Correcte", f"Bot '{bot_id}' pujat/actualitzat correctament")
    except Exception as e:
        messagebox.showerror("Error", f"No s'ha pogut pujar el bot: {e}")

def iniciar_bot(bot_id):
    if bot_id in BOTS_PROCESSES:
        return False, "Bot ja s'està executant"
    bot_path = os.path.join(BOTS_DIR, bot_id)
    scripts = [f for f in os.listdir(bot_path) if f.endswith(".py")]
    if not scripts:
        return False, "No s'ha trobat cap script .py per executar"
    script_path = os.path.join(bot_path, scripts[0])

    def runner():
        proc = subprocess.Popen(['python', script_path])
        BOTS_PROCESSES[bot_id] = proc
        proc.wait()
        BOTS_PROCESSES.pop(bot_id, None)

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    return True, "Bot iniciat correctament"

def aturar_bot(bot_id):
    proc = BOTS_PROCESSES.get(bot_id)
    if not proc:
        return False, "El bot no està executant-se"
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    BOTS_PROCESSES.pop(bot_id, None)
    return True, "Bot aturat correctament"

def eliminar_bot(listbox, bot_id):
    if messagebox.askyesno("Eliminar?", f"Segur que vols eliminar el bot '{bot_id}'?"):
        aturar_bot(bot_id)
        shutil.rmtree(os.path.join(BOTS_DIR, bot_id), ignore_errors=True)
        refrescar_bots(listbox)
        messagebox.showinfo("Eliminat", f"Bot '{bot_id}' eliminat")

def veure_info(bot_id):
    bot_path = os.path.join(BOTS_DIR, bot_id)
    scripts = [f for f in os.listdir(bot_path) if f.endswith(".py")]
    running = "Sí" if bot_id in BOTS_PROCESSES else "No"
    messagebox.showinfo("Info bot",
                        f"ID bot: {bot_id}\nScripts: {', '.join(scripts) if scripts else '(cap)'}\nEn execució: {running}")

def refrescar_bots(listbox):
    listbox.delete(0, tk.END)
    for bot in listar_bots():
        listbox.insert(tk.END, bot)

def accio_bot(listbox, accio):
    if not listbox.curselection():
        messagebox.showwarning("Error", "Selecciona un bot primer")
        return
    bot_id = listbox.get(listbox.curselection()[0])
    if accio == "start":
        success, msg = iniciar_bot(bot_id)
        if success:
            messagebox.showinfo("Iniciat", msg)
        else:
            messagebox.showerror("Error", msg)
    elif accio == "stop":
        success, msg = aturar_bot(bot_id)
        if success:
            messagebox.showinfo("Aturat", msg)
        else:
            messagebox.showerror("Error", msg)
    elif accio == "info":
        veure_info(bot_id)
    elif accio == "delete":
        eliminar_bot(listbox, bot_id)

# ------------------------ Interfície gràfica Tkinter ------------------------

def gui():
    main_win = tk.Tk()
    main_win.title("Free Hosting Bots Discord 24/7 (local)")
    main_win.geometry("650x400")

    frame_left = tk.Frame(main_win)
    frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)

    tk.Label(frame_left, text="Bots pujats:", font=("Arial", 12, "bold")).pack(anchor="w")
    listbox_bots = tk.Listbox(frame_left, width=30, height=15)
    listbox_bots.pack(fill=tk.BOTH, expand=True)
    refrescar_bots(listbox_bots)

    tk.Button(frame_left, text="Refrescar", command=lambda: refrescar_bots(listbox_bots)).pack(pady=4)
    tk.Button(frame_left, text="Pujar/Actualitzar bot", command=lambda: pujar_bot(listbox_bots)).pack(pady=4)

    frame_right = tk.Frame(main_win)
    frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=15, pady=15)

    tk.Label(frame_right, text="Accions:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))
    tk.Button(frame_right, text="Iniciar bot", width=20, command=lambda: accio_bot(listbox_bots, "start")).pack(pady=3)
    tk.Button(frame_right, text="Aturar bot", width=20, command=lambda: accio_bot(listbox_bots, "stop")).pack(pady=3)
    tk.Button(frame_right, text="Info bot", width=20, command=lambda: accio_bot(listbox_bots, "info")).pack(pady=3)
    tk.Button(frame_right, text="Eliminar bot", width=20, command=lambda: accio_bot(listbox_bots, "delete")).pack(pady=3)

    main_win.mainloop()

# ------------------------ Flask API (Control remot) ------------------------

app = Flask(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)  # Ui.logs menys

@app.route('/')
def index():
    return "Servei de bots actiu"

@app.route('/bots', methods=['GET'])
def api_listar_bots():
    bots = listar_bots()
    return jsonify(bots=bots)

@app.route('/bots/start', methods=['POST'])
def api_iniciar_bot():
    data = request.get_json()
    bot_id = data.get('bot_id')
    if not bot_id:
        return jsonify(error="No s'ha especificat bot_id"), 400
    scripts = [f for f in os.listdir(os.path.join(BOTS_DIR, bot_id)) if f.endswith(".py")]
    if not scripts:
        return jsonify(error="Bot no trobat o sense scripts"), 404
    success, msg = iniciar_bot(bot_id)
    return jsonify(message=msg), 200 if success else 400

@app.route('/bots/stop', methods=['POST'])
def api_aturar_bot():
    data = request.get_json()
    bot_id = data.get('bot_id')
    if not bot_id:
        return jsonify(error="No s'ha especificat bot_id"), 400
    success, msg = aturar_bot(bot_id)
    return jsonify(message=msg), 200 if success else 400

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# ------------------------ Entrada principal ------------------------

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    gui()
