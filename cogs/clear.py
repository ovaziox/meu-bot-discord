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

        # Limite entre 1 e 250
        if amount < 1 or amount > 250:
            msg = "❌ O número de mensagens deve estar entre **1 e 250**!"
            if ctx.interaction:
                try:
                    await ctx.interaction.response.send_message(msg, ephemeral=True)
                except discord.InteractionResponded:
                    await ctx.followup.send(msg, ephemeral=True)
            else:
                await ctx.reply(msg, delete_after=5)
            return

        # Defer se for slash command
        if ctx.interaction:
            try:
                await ctx.interaction.response.defer(ephemeral=True)
            except discord.InteractionResponded:
                pass  # Se já respondeu, ignora o erro

        # Deleta mensagens que não estão fixadas
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: not m.pinned)

        # Mensagem de confirmação
        message = f"✅ **{len(deleted)} mensagens apagadas com sucesso!**"

        # Envia mensagem dependendo do tipo de comando
        try:
            if ctx.interaction:
                await ctx.followup.send(message, ephemeral=True)
            else:
                confirm_msg = await ctx.reply(message)
                await confirm_msg.delete(delay=3)
        except Exception as e:
            print(f"[ERRO] Falha ao enviar mensagem de confirmação: {e}")

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            msg = "❌ Você não tem permissão para usar esse comando!"
            if ctx.interaction:
                try:
                    await ctx.interaction.response.send_message(msg, ephemeral=True)
                except discord.InteractionResponded:
                    await ctx.followup.send(msg, ephemeral=True)
            else:
                await ctx.reply(msg, delete_after=5)

async def setup(bot):
    await bot.add_cog(ClearCog(bot))
