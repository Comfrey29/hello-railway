import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import shutil

BOTS_DIR = "bots"
BOTS_PROCESSES = {}

if not os.path.exists(BOTS_DIR):
    os.makedirs(BOTS_DIR)

def listar_bots():
    return os.listdir(BOTS_DIR)

def subir_bot(listbox_bots):
    bot_id = simpledialog.askstring("Nombre del bot", "Introduce un nombre identificador para este bot:")
    if not bot_id:
        return
    file_path = filedialog.askopenfilename(
        title="Elige el archivo .py del bot",
        filetypes=[("Archivos Python", "*.py")]
    )
    if not file_path:
        return
    bot_path = os.path.join(BOTS_DIR, bot_id)
    os.makedirs(bot_path, exist_ok=True)  # No borramos carpeta existente
    out_path = os.path.join(bot_path, os.path.basename(file_path))
    with open(file_path, "rb") as fsrc, open(out_path, "wb") as fdst:
        fdst.write(fsrc.read())
    if bot_id not in listbox_bots.get(0, tk.END):
        listbox_bots.insert(tk.END, bot_id)
    messagebox.showinfo("Correcto", f"¡Bot '{bot_id}' subido/actualizado correctamente!")

def iniciar_bot(bot_id, script_file):
    if bot_id in BOTS_PROCESSES:
        messagebox.showinfo("Info", f"El bot '{bot_id}' ya se está ejecutando.")
        return
    bot_script_path = os.path.join(BOTS_DIR, bot_id, script_file)
    def run():
        proc = subprocess.Popen(['python', bot_script_path])
        BOTS_PROCESSES[bot_id] = proc
        proc.wait()
        if bot_id in BOTS_PROCESSES:  # Detenido
            del BOTS_PROCESSES[bot_id]
    t = threading.Thread(target=run, daemon=True)
    t.start()

def detener_bot(bot_id):
    proc = BOTS_PROCESSES.get(bot_id)
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        del BOTS_PROCESSES[bot_id]
        messagebox.showinfo("Detenido", f"Bot '{bot_id}' detenido.")
    else:
        messagebox.showwarning("No activo", f"El bot '{bot_id}' no se está ejecutando.")

def eliminar_bot(listbox, bot_id):
    if messagebox.askyesno("¿Eliminar?", f"¿Seguro que deseas eliminar el bot '{bot_id}'?"):
        detener_bot(bot_id)
        shutil.rmtree(os.path.join(BOTS_DIR, bot_id), ignore_errors=True)
        refrescar_bots(listbox)
        messagebox.showinfo("Eliminado", f"Bot '{bot_id}' eliminado.")

def ver_info(bot_id):
    bot_path = os.path.join(BOTS_DIR, bot_id)
    scripts = [f for f in os.listdir(bot_path) if f.endswith('.py')]
    running = "Sí" if bot_id in BOTS_PROCESSES else "No"
    messagebox.showinfo(
        "Info bot",
        f"Bot ID: {bot_id}\nScripts: {', '.join(scripts) if scripts else '(ninguno)'}\nEn ejecución: {running}"
    )

def refrescar_bots(listbox):
    listbox.delete(0, tk.END)
    for bot_id in listar_bots():
        listbox.insert(tk.END, bot_id)

def accion_bot(listbox, accion):
    if not listbox.curselection():
        messagebox.showwarning("Error", "Selecciona un bot primero.")
        return
    bot_id = listbox.get(listbox.curselection()[0])
    bot_path = os.path.join(BOTS_DIR, bot_id)
    scripts = [f for f in os.listdir(bot_path) if f.endswith('.py')]
    if not scripts:
        messagebox.showerror("Error", f"No hay ningún script .py en el bot '{bot_id}'")
        return
    script = scripts[0]  # Tomamos el primero
    if accion == "start":
        iniciar_bot(bot_id, script)
        messagebox.showinfo("Iniciado", f"Se ha iniciado el bot '{bot_id}'.")
    elif accion == "stop":
        detener_bot(bot_id)
    elif accion == "info":
        ver_info(bot_id)
    elif accion == "delete":
        eliminar_bot(listbox, bot_id)

def gui():
    main_window = tk.Tk()
    main_window.title("Free Hosting Bots Discord 24/7 (local)")
    main_window.geometry("650x400")

    frame_left = tk.Frame(main_window)
    frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
    tk.Label(frame_left, text="Bots subidos:", font=("Arial", 12, "bold")).pack(anchor="w")
    listbox_bots = tk.Listbox(frame_left, width=30, height=15)
    listbox_bots.pack(fill=tk.BOTH, expand=True)
    refrescar_bots(listbox_bots)

    tk.Button(frame_left, text="Refrescar", command=lambda: refrescar_bots(listbox_bots)).pack(pady=4)
    tk.Button(frame_left, text="Subir/Actualizar bot", command=lambda: subir_bot(listbox_bots)).pack(pady=4)

    frame_right = tk.Frame(main_window)
    frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=15, pady=15)
    tk.Label(frame_right, text="Acciones:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))
    tk.Button(frame_right, text="Iniciar bot", width=20, command=lambda: accion_bot(listbox_bots, "start")).pack(pady=3)
    tk.Button(frame_right, text="Detener bot", width=20, command=lambda: accion_bot(listbox_bots, "stop")).pack(pady=3)
    tk.Button(frame_right, text="Info bot", width=20, command=lambda: accion_bot(listbox_bots, "info")).pack(pady=3)
    tk.Button(frame_right, text="Eliminar bot", width=20, command=lambda: accion_bot(listbox_bots, "delete")).pack(pady=3)

    main_window.mainloop()

if __name__ == "__main__":
    gui()
