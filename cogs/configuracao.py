import discord
from discord.ext import commands
from discord import app_commands

class Configuracao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando de texto com prefixo (ex: #configuracao)
    @commands.command(name="configuracao")
    async def config_comando_texto(self, ctx):
        await ctx.send("🔧 Painel de configuração aqui! (comando de texto)")

    # Slash command (ex: /configuracao)
    @app_commands.command(name="configuracao", description="Abrir painel de configuração do bot")
    async def config_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔧 Painel de configuração aqui! (slash command)", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Configuracao(bot))
