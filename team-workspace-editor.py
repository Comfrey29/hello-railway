#!/usr/bin/env python3
import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import shutil
import requests

# Ruta local per emmagatzemar bots
BOTS_DIR = "bots"
# Diccionari per controlar processos dels bots en execució
BOTS_PROCESSES = {}
# URL base de la API desplegada a Render (modifica-la amb la teva adreça real)
RENDER_API_URL = "https://arcom-host.example.com"  # <-- posa aquí la teva URL

# Funció per validar token fent crida a l'API Render
def validar_token_api(token):
    try:
        resp = requests.post(f"{RENDER_API_URL}/validate_token", json={"token": token})
        if resp.status_code == 200 and resp.json().get("valid"):
            return True
        else:
            return False
    except Exception as e:
        print("Error validant token via API:", e)
        return False

# Funció per demanar al usuari token i validar-lo amb la API
def pedir_token_api(bot_id):
    while True:
        token = simpledialog.askstring("Token Discord", f"Introduce el token para el bot '{bot_id}':", show="*")
        if not token:
            messagebox.showwarning("Cancelado", "No se informó ningún token. Operación cancelada.")
            return False
        if validar_token_api(token):
            token_path = os.path.join(BOTS_DIR, bot_id, "token.txt")
            with open(token_path, "w") as f:
                f.write(token.strip())
            messagebox.showinfo("Éxito", "Token validado y guardado correctamente.")
            return True
        else:
            messagebox.showerror("Error", "Token inválido. Inténtelo de nuevo.")

def listar_bots():
    try:
        return os.listdir(BOTS_DIR)
    except Exception:
        return []

def subir_bot(listbox):
    bot_id = simpledialog.askstring("Nuevo Bot", "Introduce un identificador único para el bot:")
    if not bot_id:
        return
    file_path = filedialog.askopenfilename(title="Selecciona el archivo .py del bot", filetypes=[("Archivos Python","*.py")])
    if not file_path:
        return
    bot_folder = os.path.join(BOTS_DIR, bot_id)
    os.makedirs(bot_folder, exist_ok=True)
    dest_path = os.path.join(bot_folder, os.path.basename(file_path))
    try:
        shutil.copyfile(file_path, dest_path)
        if bot_id not in listbox.get(0, tk.END):
            listbox.insert(tk.END, bot_id)
        if pedir_token_api(bot_id):
            messagebox.showinfo("Información", f"Bot '{bot_id}' subido correctamente y token guardado.")
        else:
            messagebox.showwarning("Aviso", f"Bot '{bot_id}' subido, pero token no guardado o inválido.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo subir el bot: {e}")

def iniciar_bot(bot_id, script_file):
    if bot_id in BOTS_PROCESSES:
        messagebox.showinfo("Aviso", "El bot ya está en ejecución.")
        return False, "Bot activo"
    bot_folder = os.path.join(BOTS_DIR, bot_id)
    token_path = os.path.join(bot_folder, "token.txt")
    if not os.path.isfile(token_path):
        messagebox.showerror("Error", "No existe token para este bot. Debe introducirlo.")
        return False, "Sin token"
    script_path = os.path.join(bot_folder, script_file)
    if not os.path.isfile(script_path):
        return False, "Script no encontrado"

    def run():
        proc = subprocess.Popen(['python3', script_path])
        BOTS_PROCESSES[bot_id] = proc
        proc.wait()
        if bot_id in BOTS_PROCESSES:
            del BOTS_PROCESSES[bot_id]

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return True, "Bot iniciado"

def detener_bot(bot_id):
    proc = BOTS_PROCESSES.get(bot_id)
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
        del BOTS_PROCESSES[bot_id]
        messagebox.showinfo("Info", f"Bot '{bot_id}' detenido")
        return True, "Detenido"
    else:
        messagebox.showwarning("Aviso", "Bot no en ejecución")
        return False, "No estaba activo"

def eliminar_bot(listbox, bot_id):
    if messagebox.askyesno("Confirmar", f"¿Eliminar bot '{bot_id}'?"):
        detener_bot(bot_id)
        shutil.rmtree(os.path.join(BOTS_DIR, bot_id), ignore_errors=True)
        refrescar_bots(listbox)
        messagebox.showinfo("Info", "Bot eliminado")

def ver_info(bot_id):
    bot_folder = os.path.join(BOTS_DIR, bot_id)
    scripts = [f for f in os.listdir(bot_folder) if f.endswith(".py")]
    running = "Sí" if bot_id in BOTS_PROCESSES else "No"
    messagebox.showinfo("Información del bot", f"ID: {bot_id}\nScripts: {', '.join(scripts)}\nEjecutando: {running}")

def refrescar_bots(listbox):
    listbox.delete(0, tk.END)
    for bot in listar_bots():
        listbox.insert(tk.END, bot)

def accion_bot(listbox, accion):
    if not listbox.curselection():
        messagebox.showwarning("Aviso", "Seleccione un bot")
        return
    bot_id = listbox.get(listbox.curselection()[0])
    bot_folder = os.path.join(BOTS_DIR, bot_id)
    scripts = [f for f in os.listdir(bot_folder) if f.endswith(".py")]
    if not scripts:
        messagebox.showerror("Error", "No hay script para este bot")
        return
    script = scripts[0]
    if accion == "start":
        exito, msg = iniciar_bot(bot_id, script)
        if exito:
            messagebox.showinfo("Info", msg)
        else:
            messagebox.showerror("Error", msg)
    elif accion == "stop":
        detener_bot(bot_id)
    elif accion == "info":
        ver_info(bot_id)
    elif accion == "delete":
        eliminar_bot(listbox, bot_id)

def gui():
    root = tk.Tk()
    root.title("Gestor Bots Discord")
    root.geometry("700x400")

    left_frame = tk.Frame(root)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    tk.Label(left_frame, text="Bots subidos", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")
    listbox = tk.Listbox(left_frame, width=30, height=15)
    listbox.grid(row=1, column=0, columnspan=3, sticky="nsew")

    refrescar_bots(listbox)

    tk.Button(left_frame, text="Refrescar", command=lambda: refrescar_bots(listbox)).grid(row=2, column=0, sticky="ew", pady=5, padx=2)
    tk.Button(left_frame, text="Subir/Actualizar", command=lambda: subir_bot(listbox)).grid(row=2, column=1, sticky="ew", pady=5, padx=2)
    tk.Button(left_frame, text="Introducir token", command=lambda: pedir_token_api("Global")).grid(row=2, column=2, sticky="ew", pady=5, padx=2)

    root.grid_columnconfigure(0, weight=3)
    root.grid_rowconfigure(0, weight=1)

    right_frame = tk.Frame(root)
    right_frame.grid(row=0, column=1, sticky="ns", padx=10, pady=10)

    tk.Label(right_frame, text="Acciones", font=("Arial", 14, "bold")).pack(pady=5)
    tk.Button(right_frame, text="Iniciar", width=20, command=lambda: accion_bot(listbox, "start")).pack(pady=5)
    tk.Button(right_frame, text="Detener", width=20, command=lambda: accion_bot(listbox, "stop")).pack(pady=5)
    tk.Button(right_frame, text="Info", width=20, command=lambda: accion_bot(listbox, "info")).pack(pady=5)
    tk.Button(right_frame, text="Eliminar", width=20, command=lambda: accion_bot(listbox, "delete")).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    gui()
