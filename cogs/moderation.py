import discord
from discord.ext import commands

class Moderation(commands.Cog):
    """Cog que contém comandos de moderação"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Expulsa um membro do servidor"""
        try:
            await member.kick(reason=reason)
            await ctx.send(f'{member.name} foi expulso. Motivo: {reason}')
        except discord.Forbidden:
            await ctx.send("Não tenho permissão para expulsar esse usuário.")
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: {e}")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bane um membro do servidor"""
        try:
            await member.ban(reason=reason)
            await ctx.send(f'{member.name} foi banido. Motivo: {reason}')
        except discord.Forbidden:
            await ctx.send("Não tenho permissão para banir esse usuário.")
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: {e}")

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_id: int):
        """Desbane um membro pelo ID"""
        banned_users = await ctx.guild.bans()
        member = discord.utils.find(lambda u: u.user.id == member_id, banned_users)
        if member:
            await ctx.guild.unban(member.user)
            await ctx.send(f'{member.user.name} foi desbanido.')
        else:
            await ctx.send('Usuário não encontrado na lista de banidos.')

# Adiciona a Cog ao bot
async def setup(bot):
    await bot.add_cog(Moderation(bot))
