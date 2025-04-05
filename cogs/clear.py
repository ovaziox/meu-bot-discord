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
        quantidade: Optional[int] = None,
        user: Optional[discord.Member] = None
    ):
        """Apaga mensagens (até 250) do canal, podendo filtrar por usuário"""

        # Se for prefixo, tenta extrair quantidade e user da mensagem manualmente
        if not ctx.interaction:
            args = ctx.message.content.split()
            if quantidade is None:
                if len(args) > 1:
                    try:
                        quantidade = int(args[1])
                    except ValueError:
                        await ctx.reply("❌ Especifique um número válido de mensagens!", delete_after=5)
                        return
                else:
                    await ctx.reply("❌ Você precisa especificar a quantidade de mensagens!", delete_after=5)
                    return

            if user is None and len(ctx.message.mentions) > 0:
                user = ctx.message.mentions[0]

        # Verifica os limites
        if quantidade is None or quantidade < 1 or quantidade > 250:
            msg = "❌ O número de mensagens deve estar entre **1 e 250**!"
            if ctx.interaction:
                try:
                    await ctx.interaction.response.send_message(msg, ephemeral=True)
                except discord.InteractionResponded:
                    await ctx.followup.send(msg, ephemeral=True)
            else:
                await ctx.reply(msg, delete_after=5)
            return

        # Defer para slash
        if ctx.interaction:
            try:
                await ctx.interaction.response.defer(ephemeral=True)
            except discord.InteractionResponded:
                pass

        # Filtro de mensagens
        def check(msg):
            return not msg.pinned and (user is None or msg.author == user)

        # Executa limpeza
        await ctx.channel.purge(limit=quantidade, check=check)

        # Confirmação
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
