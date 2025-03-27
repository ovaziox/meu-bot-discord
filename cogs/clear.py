import discord
from discord.ext import commands

class ClearCog(commands.Cog):
    """Comando para limpar mensagens"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)  # Apenas quem tem permissão pode usar
    async def clear(self, ctx, amount: int):
        """Apaga uma quantidade específica de mensagens no canal"""
        
        # Limita o número de mensagens entre 1 e 1000
        if amount < 1 or amount > 1000:
            await ctx.send("❌ O número de mensagens deve estar entre **1 e 1000**!", delete_after=5)
            return
        
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"✅ **{amount} mensagens apagadas!**", delete_after=3)  # Mensagem temporária

async def setup(bot):
    await bot.add_cog(ClearCog(bot))
