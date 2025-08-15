import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import shutil

from flask import Flask, request, jsonify
import logging
from threading import Thread

# Directori i variable global per a processos
BOTS_DIR = "bots"
BOTS_PROCESSES = {}

# Crear directori si no existeix
if not os.path.exists(BOTS_DIR):
    os.makedirs(BOTS_DIR)

# Funcions de gestió de bots per a la GUI i API

def listar_bots():
    return os.listdir(BOTS_DIR)

def pujar_bot(listbox_bots):
    bot_id = simpledialog.askstring("Nom del bot", "Introdueix un nom identificador per aquest bot:")
    if not bot_id:
        return
    file_path = filedialog.askopenfilename(
        title="Tria l'arxiu .py del bot",
        filetypes=[("Arxius Python", "*.py")]
    )
    if not file_path:
        return
    bot_path = os.path.join(BOTS_DIR, bot_id)
    os.makedirs(bot_path, exist_ok=True)  # No esborrem carpeta existent
    out_path = os.path.join(bot_path, os.path.basename(file_path))
    with open(file_path, "rb") as fsrc, open(out_path, "wb") as fdst:
        fdst.write(fsrc.read())
    if bot_id not in listbox_bots.get(0, tk.END):
        listbox_bots.insert(tk.END, bot_id)
    messagebox.showinfo("Correcte", f"Bot '{bot_id}' pujat/actualitzat correctament!")

def iniciar_bot(bot_id, script_file):
    if bot_id in BOTS_PROCESSES:
        messagebox.showinfo("Info", f"El bot '{bot_id}' ja s'està executant.")
        return False, "Ja en execució"
    bot_script_path = os.path.join(BOTS_DIR, bot_id, script_file)
    if not os.path.isfile(bot_script_path):
        return False, "Script no trobat"

    def run():
        proc = subprocess.Popen(['python', bot_script_path])
        BOTS_PROCESSES[bot_id] = proc
        proc.wait()
        if bot_id in BOTS_PROCESSES:
            del BOTS_PROCESSES[bot_id]

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return True, "Bot iniciat"

def aturar_bot(bot_id):
    proc = BOTS_PROCESSES.get(bot_id)
    if not proc:
        return False, "Bot no està en execució"
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    del BOTS_PROCESSES[bot_id]
    return True, "Bot aturat"

def eliminar_bot(listbox, bot_id):
    if messagebox.askyesno("Eliminar?", f"Segur que vols eliminar el bot '{bot_id}'?"):
        aturar_bot(bot_id)
        shutil.rmtree(os.path.join(BOTS_DIR, bot_id), ignore_errors=True)
        refrescar_bots(listbox)
        messagebox.showinfo("Eliminat", f"Bot '{bot_id}' eliminat.")

def veure_info(bot_id):
    bot_path = os.path.join(BOTS_DIR, bot_id)
    scripts = [f for f in os.listdir(bot_path) if f.endswith('.py')]
    running = "Sí" if bot_id in BOTS_PROCESSES else "No"
    messagebox.showinfo(
        "Info bot",
        f"ID bot: {bot_id}\nScripts: {', '.join(scripts) if scripts else '(cap)'}\nEn execució: {running}"
    )

def refrescar_bots(listbox):
    listbox.delete(0, tk.END)
    for bot_id in listar_bots():
        listbox.insert(tk.END, bot_id)

def accio_bot(listbox, accio):
    if not listbox.curselection():
        messagebox.showwarning("Error", "Selecciona un bot primer.")
        return
    bot_id = listbox.get(listbox.curselection()[0])
    bot_path = os.path.join(BOTS_DIR, bot_id)
    scripts = [f for f in os.listdir(bot_path) if f.endswith('.py')]
    if not scripts:
        messagebox.showerror("Error", f"No hi ha cap script .py al bot '{bot_id}'")
        return
    script = scripts  # Agafem el primer
    if accio == "start":
        success, msg = iniciar_bot(bot_id, script)
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

def gui():
    main_window = tk.Tk()
    main_window.title("Free Hosting Bots Discord 24/7 (local)")
    main_window.geometry("650x400")

    frame_left = tk.Frame(main_window)
    frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
    tk.Label(frame_left, text="Bots pujats:", font=("Arial", 12, "bold")).pack(anchor="w")
    listbox_bots = tk.Listbox(frame_left, width=30, height=15)
    listbox_bots.pack(fill=tk.BOTH, expand=True)
    refrescar_bots(listbox_bots)

    tk.Button(frame_left, text="Refrescar", command=lambda: refrescar_bots(listbox_bots)).pack(pady=4)
    tk.Button(frame_left, text="Pujar/Actualitzar bot", command=lambda: pujar_bot(listbox_bots)).pack(pady=4)

    frame_right = tk.Frame(main_window)
    frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=15, pady=15)
    tk.Label(frame_right, text="Accions:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))
    tk.Button(frame_right, text="Iniciar bot", width=20, command=lambda: accio_bot(listbox_bots, "start")).pack(pady=3)
    tk.Button(frame_right, text="Aturar bot", width=20, command=lambda: accio_bot(listbox_bots, "stop")).pack(pady=3)
    tk.Button(frame_right, text="Info bot", width=20, command=lambda: accio_bot(listbox_bots, "info")).pack(pady=3)
    tk.Button(frame_right, text="Eliminar bot", width=20, command=lambda: accio_bot(listbox_bots, "delete")).pack(pady=3)

    main_window.mainloop()

# -------- Flask API per control remot --------
app = Flask(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)  # Reducir logs

@app.route('/bots', methods=['GET'])
def api_listar_bots():
    bots = listar_bots()
    return jsonify({"bots": bots})

@app.route('/bots/start', methods=['POST'])
def api_iniciar_bot():
    data = request.get_json()
    bot_id = data.get('bot_id')
    if not bot_id:
        return jsonify({"error": "No s'ha especificat bot_id"}), 400
    scripts = [f for f in os.listdir(os.path.join(BOTS_DIR, bot_id)) if f.endswith('.py')]
    if not scripts:
        return jsonify({"error": "Bot no trobat o sense scripts"}), 404
    success, msg = iniciar_bot(bot_id, scripts[0])
    status = 200 if success else 400
    return jsonify({"message": msg}), status

@app.route('/bots/stop', methods=['POST'])
def api_aturar_bot():
    data = request.get_json()
    bot_id = data.get('bot_id')
    if not bot_id:
        return jsonify({"error": "No s'ha especificat bot_id"}), 400
    success, msg = aturar_bot(bot_id)
    status = 200 if success else 400
    return jsonify({"message": msg}), status

@app.route('/')
def api_index():
    return "Servei de bots actiu"

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# -------- Inici dels dos serveis --------
if __name__ == "__main__":
    # Executar Flask en un fil separat
    Thread(target=run_flask, daemon=True).start()
    # Executar la GUI localment
    gui()
