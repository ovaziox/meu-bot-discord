import discord
from discord.ext import commands
from typing import Optional

class ClearCog(commands.Cog):
    """Comando para limpar mensagens"""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="clear",
        description="Apaga mensagens do canal (opcionalmente de um usuário específico)"
    )
    @commands.has_permissions(manage_messages=True)
    async def clear(
        self,
        ctx: commands.Context,
        amount: int,
        member: Optional[discord.Member] = None
    ):
        """Apaga mensagens (até 250) do canal, podendo filtrar por usuário"""

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

        # Defer (necessário para slash commands)
        if ctx.interaction:
            try:
                await ctx.interaction.response.defer(ephemeral=True)
            except discord.InteractionResponded:
                pass

        # Define a função de filtro
        def check(msg):
            return not msg.pinned and (member is None or msg.author == member)

        # Executa a limpeza
        await ctx.channel.purge(limit=amount, check=check)

        # Confirmação sem número de mensagens
        confirm_msg = "✅ Mensagens apagadas com sucesso!"

        try:
            if ctx.interaction:
                await ctx.followup.send(confirm_msg, ephemeral=True)
            else:
                msg = await ctx.reply(confirm_msg)
                await msg.delete(delay=3)
        except Exception as e:
            print(f"[ERRO] Falha ao enviar confirmação: {e}")

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
