import os
import asyncio
import tkinter as tk
from tkinter import messagebox, filedialog
from dotenv import load_dotenv
import discord
import requests

# Carregar variables del .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SERVICE_ID = os.getenv("SERVICE_ID")
API_KEY = os.getenv("API_KEY")

if not DISCORD_TOKEN or not SERVICE_ID or not API_KEY:
    raise ValueError("Falten DISCORD_TOKEN, SERVICE_ID o API_KEY al .env")

# Configuració del client Discord
intents = discord.Intents.default()
intents.message_content = True  # necessaris si vols llegir missatges
client = discord.Client(intents=intents)
discord_task = None

# Funcions de Discord
async def start_bot_async():
    try:
        await client.login(DISCORD_TOKEN)
        print("Token de Discord correcte ✅")
        await client.connect()
    except discord.LoginFailure:
        messagebox.showerror("Error", "Token de Discord incorrecte ❌")
    except Exception as e:
        messagebox.showerror("Error", f"Error al connectar Discord: {e}")

def start_bot():
    global discord_task
    if discord_task is None or discord_task.done():
        discord_task = asyncio.create_task(start_bot_async())

def stop_bot():
    if client.is_ready():
        asyncio.create_task(client.close())
        messagebox.showinfo("Info", "Bot de Discord aturat ✅")

# Funció de Deploy a Render
def deploy_render():
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {"clearCache": False}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        messagebox.showinfo("Deploy Render", "Deploy iniciat correctament ✅")
    elif response.status_code == 401:
        messagebox.showerror("Deploy Render", "Error 401: Unauthorized. Revisa API_KEY i SERVICE_ID ❌")
    else:
        messagebox.showerror("Deploy Render", f"Error {response.status_code}: {response.text}")

# GUI amb Tkinter
root = tk.Tk()
root.title("Team Workspace Editor")

tk.Button(root, text="Engegar Bot Discord", command=start_bot).pack(pady=5)
tk.Button(root, text="Parar Bot Discord", command=stop_bot).pack(pady=5)
tk.Button(root, text="Deploy Render", command=deploy_render).pack(pady=5)
tk.Button(root, text="Info", command=lambda: messagebox.showinfo("Info", "Team Workspace Editor amb Discord i Render")).pack(pady=5)

root.mainloop()

Compose