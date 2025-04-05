import discord
from discord.ext import commands
import config
import json
import os
import asyncio

intents = discord.Intents.all()

# Carrega os prefixos de prefixos.json
def carregar_prefixos():
    if not os.path.exists("prefixos.json"):
        with open("prefixos.json", "w") as f:
            json.dump({}, f)
    with open("prefixos.json", "r") as f:
        return json.load(f)

prefixos_por_servidor = carregar_prefixos()

# Prefixo dinâmico
async def get_prefix(bot, message):
    if message.guild:
        return prefixos_por_servidor.get(str(message.guild.id), config.PREFIX)
    return config.PREFIX

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# Carrega os comandos (Cogs)
async def main():
    async with bot:
        for arquivo in os.listdir("./cogs"):
            if arquivo.endswith(".py"):
                try:
                    await bot.load_extension(f"cogs.{arquivo[:-3]}")
                    print(f"✅ Extensão cogs.{arquivo[:-3]} carregada com sucesso.")
                except Exception as e:
                    print(f"❌ Erro ao carregar cogs.{arquivo[:-3]}: {e}")
        await bot.start(config.TOKEN)

asyncio.run(main())
