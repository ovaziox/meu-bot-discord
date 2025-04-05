import discord
from discord.ext import commands
import os
import json
import asyncio
from config import TOKEN  # Importa o token do config.py

PREFIXO_PATH = "data/prefixos.json"


def get_prefix(bot, message):
    try:
        with open(PREFIXO_PATH, "r") as f:
            prefixos = json.load(f)
        return prefixos.get(str(message.guild.id), "#")
    except:
        return "#"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    for guild in bot.guilds:
        try:
            with open(PREFIXO_PATH, "r") as f:
                prefixos = json.load(f)
            prefixo = prefixos.get(str(guild.id), "#")
            print(f"🔧 Servidor: {guild.name} | Prefixo atual: {prefixo}")
        except Exception as e:
            print(f"Erro ao ler prefixo: {e}")

async def carregar_cogs():
    for arquivo in os.listdir("cogs"):
        if arquivo.endswith(".py") and not arquivo.startswith("__"):
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
