import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# Caminho do arquivo de prefixos
PREFIXO_PATH = "prefixos.json"

def salvar_prefixo(guild_id: int, novo_prefixo: str):
    with open(PREFIXO_PATH, "r") as f:
        prefixos = json.load(f)
    prefixos[str(guild_id)] = novo_prefixo
    with open(PREFIXO_PATH, "w") as f:
        json.dump(prefixos, f, indent=4)

class Configuracao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="config", help="Altere o prefixo do bot")
    async def config_prefixo_texto(self, ctx, novo_prefixo: str):
        salvar_prefixo(ctx.guild.id, novo_prefixo)
        await ctx.send(f"✅ Prefixo alterado para `{novo_prefixo}` com sucesso!")

    @app_commands.command(name="config", description="Altere o prefixo do bot")
    @app_commands.describe(novo_prefixo="Novo prefixo para o bot")
    async def config_prefixo_slash(self, interaction: discord.Interaction, novo_prefixo: str):
        salvar_prefixo(interaction.guild.id, novo_prefixo)
        await interaction.response.send_message(f"✅ Prefixo alterado para `{novo_prefixo}` com sucesso!", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            synced = await self.bot.tree.sync()
            print(f"🌐 Slash commands sincronizados: {len(synced)} comandos")
        except Exception as e:
            print(f"Erro ao sincronizar comandos slash: {e}")

async def setup(bot):
    await bot.add_cog(Configuracao(bot))
