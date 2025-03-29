import discord
from discord.ext import commands
import config  # Importa configurações do bot
import asyncio

# Configuração dos intents do bot
intents = discord.Intents.default()
intents.message_content = True  # Necessário para comandos baseados em mensagens
intents.guilds = True  # Permite que o bot veja servidores
intents.members = True  # Para comandos de moderação

# Define o bot com o prefixo configurado no config.py
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

# Evento chamado quando o bot fica online
@bot.event
async def on_ready():
    # Sincroniza os comandos híbridos (incluindo slash commands)
    await bot.tree.sync()  # Registra os comandos na árvore do Discord
    print(f'✅ Bot conectado como {bot.user.name}')

# Função para carregar todas as Cogs
async def load_extensions():
    initial_extensions = ["cogs.test", "cogs.ticket", "cogs.clear", "cogs.say", "cogs.configuracao"]  # Lista de Cogs
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"✅ Extensão {extension} carregada com sucesso.")
        except Exception as e:
            print(f"❌ Erro ao carregar {extension}: {e}")

# Inicializa o bot assincronamente
async def main():
    async with bot:
        await load_extensions()
        await bot.start(config.TOKEN)

# Executa a função assíncrona principal
asyncio.run(main())
