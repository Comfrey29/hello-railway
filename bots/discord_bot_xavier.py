import discord
from discord.ext import commands

# Configura el bot amb el prefix que vulguis
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# Comando clásico con @bot.command
@bot.command(name="info")
async def info(ctx):
    guild = ctx.guild  # Servidor donde se ejecuta el comando
    nombre = guild.name
    miembros = guild.member_count
    creador = guild.owner
    creado_el = guild.created_at.strftime("%d/%m/%Y")
    canales_texto = len(guild.text_channels)
    canales_voz = len(guild.voice_channels)

    embed = discord.Embed(
        title=f"📌 Información de {nombre}",
        color=discord.Color.green()
    )
    embed.add_field(name="👑 Dueño", value=str(creador), inline=False)
    embed.add_field(name="👥 Miembros", value=miembros, inline=True)
    embed.add_field(name="💬 Canales de texto", value=canales_texto, inline=True)
    embed.add_field(name="🔊 Canales de voz", value=canales_voz, inline=True)
    embed.add_field(name="📅 Creado el", value=creado_el, inline=False)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)

    await ctx.send(embed=embed)

# Ejecutar el bot
TOKEN = 
bot.run(TOKEN)
