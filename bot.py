import discord
from discord.ext import commands
import os
import json
import asyncio
from config import TOKEN  # Importa o token do config.py

PREFIXO_PATH = "data/prefixos.json"


from discord.ext import commands
import json

def get_prefix(bot, message):
    try:
        with open("data/prefixos.json", "r") as f:
            prefixos = json.load(f)
        return prefixos.get(str(message.guild.id), "#")
    except:
        return "#"

bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🤖 Bot online como {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"🌐 {len(synced)} slash commands sincronizados.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos slash: {e}")


async def carregar_cogs():
    for arquivo in os.listdir("cogs"):
        if arquivo.endswith(".py") and not arquivo.startswith("__init__"):
            try:
                await bot.load_extension(f"cogs.{arquivo[:-3]}")
                print(f"✅ Extensão cogs.{arquivo[:-3]} carregada com sucesso.")
            except Exception as e:
                print(f"❌ Erro ao carregar cogs.{arquivo[:-3]}: {e}")


async def main():
    async with bot:
        await carregar_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
