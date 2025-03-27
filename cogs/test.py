import discord
from discord.ext import commands

class Test(commands.Cog):
    """Cog para testar se o bot está online"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Responde com Pong! e apaga o comando do usuário"""
        try:
            await ctx.message.delete()  # Apaga a mensagem do usuário
        except discord.Forbidden:
            print("❌ O bot não tem permissão para deletar mensagens!")

        latency = round(self.bot.latency * 1000)  # Converte para milissegundos
        await ctx.send(f"Pong! 🏓 Latência: {latency}ms")

# Adiciona a Cog ao bot
async def setup(bot):
    await bot.add_cog(Test(bot))
