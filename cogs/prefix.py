import discord
from discord.ext import commands
from discord import app_commands
import json
import os

PREFIXOS_PATH = "data/prefixos.json"

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        if not os.path.exists(PREFIXOS_PATH):
            with open(PREFIXOS_PATH, "w") as f:
                json.dump({}, f)

    def salvar_prefixo(self, guild_id, novo_prefixo):
        with open(PREFIXOS_PATH, "r") as f:
            prefixos = json.load(f)
        prefixos[str(guild_id)] = novo_prefixo
        with open(PREFIXOS_PATH, "w") as f:
            json.dump(prefixos, f, indent=4)

    @commands.command(name="configprefixo")
    @commands.has_permissions(administrator=True)
    async def alterar_prefixo_texto(self, ctx, novo_prefixo: str):
        """Altera o prefixo do servidor (comando de texto)"""
        self.salvar_prefixo(ctx.guild.id, novo_prefixo)
        await ctx.send(f"✅ Prefixo alterado para `{novo_prefixo}`")

    @app_commands.command(name="configprefixo", description="Altere o prefixo dos comandos (Slash Command)")
    @app_commands.checks.has_permissions(administrator=True)
    async def configprefixo_slash(self, interaction: discord.Interaction, novo_prefixo: str):
        """Slash command para alterar prefixo"""
        self.salvar_prefixo(interaction.guild.id, novo_prefixo)
        await interaction.response.send_message(f"✅ Prefixo alterado para `{novo_prefixo}`", ephemeral=True)

    async def cog_load(self):
        # Registra o slash command corretamente
        self.bot.tree.add_command(self.configprefixo_slash)

async def setup(bot):
    await bot.add_cog(Prefix(bot))
