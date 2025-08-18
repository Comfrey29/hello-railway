import os
import discord
from discord import app_commands, Interaction, File
from discord.ext import commands
from dotenv import load_dotenv
import requests
import io

# Carreguem variables del .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RENDER_API_KEY = os.getenv("RENDER_API_KEY")
SERVICE_ID = os.getenv("SERVICE_ID")

# Defineix els intents del bot
intents = discord.Intents.default()
intents.message_content = True

# Inicialitzem el bot sense command_prefix perquè només fem slash commands
bot = commands.Bot(command_prefix=None, intents=intents)

# Llista d'admins per validar permisos
ADMINS = [1297877685896216626]  # Substitueix amb IDs de Discord reals

# Funció d'ajuda per validar si l'usuari és admin
def is_admin(interaction: Interaction):
    return interaction.user.id in ADMINS

# --- COMANDES ---
@bot.event
async def on_ready():
    print(f"{bot.user} connectat!")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronitzats: {len(synced)}")
    except Exception as e:
        print(f"Error sincronitzant commands: {e}")

# Deploy amb fitxer adjunt (només admins)
@bot.tree.command(name="deploy", description="Deploy d'un fitxer .py a Render (admins only)")
@app_commands.describe(file="Fitxer Python a desplegar")
async def deploy(interaction: Interaction, file: discord.Attachment):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Només admins poden fer deploy.", ephemeral=True)
        return

    await interaction.response.send_message("Iniciant deploy a Render...", ephemeral=True)

    # Llegim contingut del fitxer
    py_content = await file.read()
    files = {"file": (file.filename, io.BytesIO(py_content))}
   
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}"
    }
    payload = {"branch": "main"}  # Només branch, no ClearCache

    response = requests.post(url, headers=headers, json=payload, files=files)
   
    if response.status_code in [200, 201]:
        await interaction.followup.send("✅ Deploy iniciat correctament!", ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Error al fer deploy: {response.status_code}\n{response.text}", ephemeral=True)

# Comanda per veure status del servei Render
@bot.tree.command(name="status", description="Mostra l'estat actual del servei Render")
async def status(interaction: Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Només admins poden consultar status.", ephemeral=True)
        return

    url = f"https://api.render.com/v1/services/{SERVICE_ID}"
    headers = {"Authorization": f"Bearer {RENDER_API_KEY}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        msg = f"**Servei:** {data['name']}\n**Estat:** {data['status']}"
        await interaction.response.send_message(msg, ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Error obtenint status: {response.status_code}", ephemeral=True)

# Llista de bots (simulada)
@bot.tree.command(name="bots", description="Llista els bots gestionats")
async def bots_list(interaction: Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Només admins poden veure la llista de bots.", ephemeral=True)
        return

    bots = ["arcomhost#3746", "tempe#1234", "comfreybot#9876"]
    await interaction.response.send_message(f"**Bots gestionats:**\n" + "\n".join(bots), ephemeral=True)

# Reiniciar un bot
@bot.tree.command(name="restart", description="Reinicia un bot gestionat")
@app_commands.describe(botname="Nom del bot a reiniciar")
async def restart(interaction: Interaction, botname: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Només admins poden reiniciar bots.", ephemeral=True)
        return

    # Aquí podria anar la crida real a Render per reiniciar
    await interaction.response.send_message(f"✅ Bot `{botname}` reiniciat correctament!", ephemeral=True)

# Veure logs simulats
@bot.tree.command(name="logs", description="Mostra els últims logs del bot/servei")
async def logs(interaction: Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Només admins poden veure logs.", ephemeral=True)
        return

    logs_text = "Últims logs:\n- Bot inicialitzat\n- Deploy completat\n- Comanda /status executada"
    await interaction.response.send_message(f"```{logs_text}```", ephemeral=True)

# Permissions (simulat)
@bot.tree.command(name="permissions", description="Gestiona permisos d'admins")
@app_commands.describe(action="afegir o treure", user="Usuari a modificar")
async def permissions(interaction: Interaction, action: str, user: discord.Member):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Només admins poden gestionar permisos.", ephemeral=True)
        return
    global ADMINS
    if action.lower() == "afegir":
        if user.id not in ADMINS:
            ADMINS.append(user.id)
            await interaction.response.send_message(f"✅ {user.name} ara és admin.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{user.name} ja és admin.", ephemeral=True)
    elif action.lower() == "treure":
        if user.id in ADMINS:
            ADMINS.remove(user.id)
            await interaction.response.send_message(f"✅ {user.name} ja no és admin.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{user.name} no era admin.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Acció desconeguda. Usa `afegir` o `treure`.", ephemeral=True)

# Executem el bot
bot.run(DISCORD_TOKEN)
