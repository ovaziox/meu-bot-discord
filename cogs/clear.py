import discord
from discord.ext import commands

class ClearCog(commands.Cog):
    """Comando para limpar mensagens"""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clear", description="Apaga uma quantidade específica de mensagens")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int):
        """Apaga uma quantidade específica de mensagens no canal"""

        if amount < 1 or amount > 1000:
            if ctx.interaction:
                await ctx.interaction.response.send_message("❌ O número de mensagens deve estar entre **1 e 1000**!", ephemeral=True)
            else:
                await ctx.reply("❌ O número de mensagens deve estar entre **1 e 1000**!", delete_after=5)
            return

        # Defer para indicar que o bot está processando (obrigatório em slash)
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)

        # Apagar as mensagens (evita fixadas)
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: not m.pinned)

        # Enviar confirmação
        message = f"✅ **{len(deleted)} mensagens apagadas com sucesso!**"
        
        if ctx.interaction:
            await ctx.followup.send(message, ephemeral=True)
        else:
            confirm_msg = await ctx.reply(message)
            await confirm_msg.delete(delay=3)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            if ctx.interaction:
                await ctx.interaction.response.send_message("❌ Você não tem permissão para usar esse comando!", ephemeral=True)
            else:
                await ctx.reply("❌ Você não tem permissão para usar esse comando!", delete_after=5)

async def setup(bot):
    await bot.add_cog(ClearCog(bot))
