import discord
from discord.ext import commands

class LumeBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say_custom")
    @commands.has_permissions(manage_messages=True)  # Permite apenas quem pode gerenciar mensagens
    async def say(self, ctx, title: str, color: str, *, message: str):
        """Comando para enviar uma mensagem formatada com embed."""

        # Verifica se a cor está no formato hexadecimal válido
        if not color.startswith("#") or len(color) != 7:
            await ctx.send("Por favor, insira uma cor no formato hexadecimal válido (#RRGGBB).", delete_after=5)
            return

        try:
            # Tenta converter a cor hexadecimal para inteiro
            embed_color = int(color[1:], 16)
        except ValueError:
            await ctx.send("A cor fornecida não é válida. Certifique-se de usar o formato hexadecimal correto (#RRGGBB).", delete_after=5)
            return

        try:
            # Cria o embed com a mensagem formatada
            embed = discord.Embed(
                title=title,
                description=message,
                color=embed_color  # Usa a cor convertida
            )

            # Verifica se o servidor tem um ícone, senão usa um ícone genérico
            footer_icon = ctx.guild.icon.url if ctx.guild.icon else None
            embed.set_footer(text="Todos os direitos reservados | LumeCraft © 2025", icon_url=footer_icon)


            # Envia a mensagem com o embed
            await ctx.send(embed=embed)

            # Apaga a mensagem original enviada pelo usuário
            await ctx.message.delete()

        except discord.errors.HTTPException as e:
            await ctx.send(f"Erro ao tentar enviar a mensagem: {e}", delete_after=5)

    @say.error
    async def say_error(self, ctx, error):
        """Tratamento de erros para o comando say."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Você precisa de permissão para gerenciar mensagens para usar esse comando.", delete_after=5)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Você usou um formato incorreto. O comando deve ser: `#say <título> <cor hexadecimal> <mensagem>`", delete_after=5)
        else:
            raise error

# Para adicionar ao seu bot
async def setup(bot):
    await bot.add_cog(LumeBot(bot))
