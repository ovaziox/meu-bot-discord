import discord
from discord.ext import commands

class LumeBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say")
    async def say(self, ctx, *, message: str):
        # Cria o embed com a mensagem formatada
        embed = discord.Embed(
            title="Mensagem do LumeBot",
            description=message,
            color=discord.Color.blue()
        )
        
        # Adiciona o footer com o ícone do servidor
        embed.set_footer(text="Copyright 2025", icon_url=ctx.guild.icon.url)
        
        # Envia a mensagem com o embed
        await ctx.send(embed=embed)
        
        # Apaga a mensagem original enviada pelo usuário
        await ctx.message.delete()

# Para adicionar ao seu bot
async def setup(bot):
    await bot.add_cog(LumeBot(bot))
