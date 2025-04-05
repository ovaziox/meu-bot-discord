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
            await ctx.reply("❌ O número de mensagens deve estar entre **1 e 1000**!", ephemeral=True if isinstance(ctx.interaction, discord.Interaction) else False, delete_after=5)
            return

        # Filtra apenas mensagens que o bot pode deletar
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: not m.pinned)

        # Envia a confirmação com a contagem real
        confirm_msg = await ctx.reply(f"✅ **{len(deleted)} mensagens apagadas com sucesso!**", ephemeral=True if isinstance(ctx.interaction, discord.Interaction) else False)
        
        # Se não for slash, deletar a confirmação após alguns segundos
        if not isinstance(ctx.interaction, discord.Interaction):
            await confirm_msg.delete(delay=3)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("❌ Você não tem permissão para usar esse comando!", ephemeral=True if isinstance(ctx.interaction, discord.Interaction) else False)

async def setup(bot):
    await bot.add_cog(ClearCog(bot))
