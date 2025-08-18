import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import shutil
import discord
import asyncio
import requests
import json
from flask import Flask

# Configuració global
BOTS_DIR = "bots"
BOTS_PROCESSES = {}

# API Key i dades de Render
RENDER_API_KEY = os.environ.get("RENDER_API_KEY")  # Agafar de variables d'entorn
OWNER_ID = os.environ.get("RENDER_OWNER_ID", "tea-d2f0nsvdiees738cq2e0")
REPO_URL = os.environ.get("RENDER_REPO", "https://github.com/Comfrey29/hello-railway.git")
RENDER_BASE_URL = "https://api.render.com/v1/services"

# Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Discord Actiu!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# Validar token de Discord
async def validar_token_discord(token):
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    try:
        await client.login(token)
        await client.close()
        return True
    except discord.errors.LoginFailure:
        return False
    except Exception as e:
        print(f"[validar_token_discord] Error: {e}")
        return False

# Deploy Render amb validació
def desplegar_a_render(bot_id, token):
    if not RENDER_API_KEY:
        messagebox.showerror("Error", "Falta la variable d'entorn RENDER_API_KEY.\n\n"
                             "Solució:\nexport RENDER_API_KEY=la_teva_clau")
        return False

    print(f"[desplegar_a_render] Deploy iniciat per bot-{bot_id}")
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json"
    }
    clean_token = token.strip().replace("\\", "")
    payload = {
        "type": "web_service",
        "name": f"bot-{bot_id}",
        "ownerId": OWNER_ID,
        "repo": REPO_URL,
        "branch": "main",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "python bot.py",
        "plan": "starter",
        "serviceDetails": {
            "env": "python",
            "envSpecificDetails": {"runtimeVersion": "3.9"}  # Versió segura
        },
        "envVars": [
            {"key": "DISCORD_TOKEN", "value": clean_token, "sync": True}
        ]
    }
    print(json.dumps(payload, indent=2))

    try:
        resp = requests.post(RENDER_BASE_URL, headers=headers, json=payload)
        resp.raise_for_status()
        print(f"[desplegar_a_render] Deploy correcte! Status: {resp.status_code}")
        return True
    except requests.exceptions.HTTPError as http_err:
        print(f"[desplegar_a_render] Error HTTP: {http_err}")
        try:
            print(f"Resposta: {resp.status_code} {resp.text}")
        except:
            pass
        messagebox.showerror("Error Render", f"Error HTTP: {http_err}\n\n{resp.text}")
        return False
    except Exception as e:
        print(f"[desplegar_a_render] Error general: {e}")
        messagebox.showerror("Error Render", f"Error inesperat: {e}")
        return False

# Sol·licitar token
def pedir_token_directo(bot_id):
    root = tk.Tk()
    root.withdraw()
    token = simpledialog.askstring("Token Discord", f"Token pel bot '{bot_id}'", show="*")
    root.destroy()
    if not token:
        messagebox.showwarning("Cancel·lat", "Token no introduït.")
        return False
    if asyncio.run(validar_token_discord(token)):
        bot_folder = os.path.join(BOTS_DIR, bot_id)
        os.makedirs(bot_folder, exist_ok=True)
        with open(os.path.join(bot_folder, "token.txt"), "w") as f:
            f.write(token.strip())
        messagebox.showinfo("Token vàlid", "Token guardat correctament.")
        if desplegar_a_render(bot_id, token):
            messagebox.showinfo("Deploy OK", "Bot allotjat correctament!")
        return True
    else:
        messagebox.showerror("Token Invàlid", "Token Discord invàlid.")
        return False

# Gestió de bots locals
def listar_bots():
    return os.listdir(BOTS_DIR) if os.path.exists(BOTS_DIR) else []

def iniciar_bot(bot_id, script):
    if bot_id in BOTS_PROCESSES:
        messagebox.showinfo("Ja actiu", f"Bot '{bot_id}' ja s'està executant.")
        return
    path = os.path.join(BOTS_DIR, bot_id, script)
    if not os.path.isfile(path):
        messagebox.showerror("Error", f"Script no trobat: {script}")
        return
    def run():
        threading.Thread(target=run_flask, daemon=True).start()
        proc = subprocess.Popen(["python3", path])
        BOTS_PROCESSES[bot_id] = proc
        proc.wait()
        BOTS_PROCESSES.pop(bot_id, None)
    threading.Thread(target=run, daemon=True).start()
    messagebox.showinfo("Iniciat", f"Bot '{bot_id}' iniciat")

def detener_bot(bot_id):
    proc = BOTS_PROCESSES.get(bot_id)
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
        BOTS_PROCESSES.pop(bot_id, None)
        messagebox.showinfo("Detingut", f"Bot '{bot_id}' aturat")
    else:
        messagebox.showinfo("Inactiu", "El bot no s'estava executant")

def eliminar_bot(listbox, bot_id):
    if messagebox.askyesno("Eliminar", f"Eliminar bot '{bot_id}'?"):
        detener_bot(bot_id)
        shutil.rmtree(os.path.join(BOTS_DIR, bot_id), ignore_errors=True)
        refrescar_bots(listbox)

def ver_info(bot_id):
    folder = os.path.join(BOTS_DIR, bot_id)
    scripts = [f for f in os.listdir(folder) if f.endswith(".py")]
    running = "Sí" if bot_id in BOTS_PROCESSES else "No"
    messagebox.showinfo("Info Bot", f"Bot: {bot_id}\nScripts: {scripts}\nExecutant-se: {running}")

def refrescar_bots(listbox):
    listbox.delete(0, tk.END)
    for bot in listar_bots():
        listbox.insert(tk.END, bot)

def accion_bot(listbox, accio):
    if not listbox.curselection():
        messagebox.showwarning("Selecciona", "Selecciona un bot")
        return
    bot_id = listbox.get(listbox.curselection()[0])
    scripts = [f for f in os.listdir(os.path.join(BOTS_DIR, bot_id)) if f.endswith(".py")]
    if not scripts:
        messagebox.showerror("Error", "No hi ha scripts .py")
        return
    script = scripts[0]
    if accio == "start":
        iniciar_bot(bot_id, script)
    elif accio == "stop":
        detener_bot(bot_id)
    elif accio == "info":
        ver_info(bot_id)
    elif accio == "delete":
        eliminar_bot(listbox, bot_id)

# GUI
def gui():
    print("[MAIN] Obrint GUI...")
    root = tk.Tk()
    root.title("Gestor Bots Discord")
    root.geometry("700x400")

    left = tk.Frame(root)
    left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    tk.Label(left, text="Bots disponibles", font=("Arial", 14)).grid(row=0, column=0, sticky="w")
    listbox = tk.Listbox(left, width=30, height=15)
    listbox.grid(row=1, column=0, columnspan=3, sticky="nsew")
    refrescar_bots(listbox)

    tk.Button(left, text="Refrescar", command=lambda: refrescar_bots(listbox)).grid(row=2, column=0, padx=2, pady=5, sticky="ew")
    tk.Button(left, text="Pujar Bot", command=lambda: simpledialog.askstring("Nou Bot", "ID del bot:") or None).grid(row=2, column=1, padx=2, pady=5, sticky="ew")
    tk.Button(left, text="Token manual", command=lambda: pedir_token_directo("Global")).grid(row=2, column=2, padx=2, pady=5, sticky="ew")

    right = tk.Frame(root)
    right.grid(row=0, column=1, sticky="ns", padx=10, pady=10)

    tk.Label(right, text="Accions", font=("Arial", 14)).pack(pady=5)
    tk.Button(right, text="Iniciar", width=20, command=lambda: accion_bot(listbox, "start")).pack(pady=5)
    tk.Button(right, text="Detenir", width=20, command=lambda: accion_bot(listbox, "stop")).pack(pady=5)
    tk.Button(right, text="Info", width=20, command=lambda: accion_bot(listbox, "info")).pack(pady=5)
    tk.Button(right, text="Eliminar", width=20, command=lambda: accion_bot(listbox, "delete")).pack(pady=5)

    root.mainloop()

# Entry point
if __name__ == "__main__":
    print("[MAIN] Inici del programa")
    os.makedirs(BOTS_DIR, exist_ok=True)
    threading.Thread(target=run_flask, daemon=True).start()
    print("[MAIN] Flask arrencat")
    gui()
