import discord
from discord.ext import commands

class SpamCog(commands.Cog):
    """Comando para spammar mensagens no canal"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="spam")
    @commands.has_permissions(administrator=True)  # Apenas administradores podem usar
    async def spam(self, ctx):
        """Envia 50 mensagens para teste"""
        for i in range(50):
            await ctx.send(f"🔹 Mensagem de teste {i+1}/50")

async def setup(bot):
    await bot.add_cog(SpamCog(bot))
