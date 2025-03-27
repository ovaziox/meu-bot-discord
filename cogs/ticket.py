import discord
from discord.ext import commands
from discord import ui
import os

class TicketButton(ui.View):
    """Cria um botão para abrir tickets"""
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.open_tickets = {}

    @ui.button(label="📩 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        user = interaction.user
        channel_name = f"ticket-{user.name.lower().replace(' ', '-')}"
        
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message("❌ Você já tem um ticket aberto!", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            discord.utils.get(guild.roles, permissions=discord.Permissions(administrator=True)): 
                discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        self.open_tickets[user.id] = ticket_channel.id

        embed = discord.Embed(
            title="🎟️ Ticket Criado",
            description=f"Olá {user.mention}, um membro da equipe irá atendê-lo em breve!\n\n🔒 Clique abaixo para fechar este ticket quando o problema for resolvido.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=CloseTicketButton(self.bot, self.open_tickets))
        await interaction.response.send_message(f"✅ Seu ticket foi criado: {ticket_channel.mention}", ephemeral=True)


class CloseTicketButton(ui.View):
    """Cria um botão para fechar tickets com confirmação"""
    def __init__(self, bot, open_tickets):
        super().__init__(timeout=None)
        self.bot = bot
        self.open_tickets = open_tickets

    @ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()  # Evita erro "Esta interação falhou"
    
        user = interaction.user
        guild = interaction.guild
        channel = interaction.channel
        
        confirm_view = ConfirmCloseView(self.bot, self.open_tickets, channel)
        await interaction.followup.send("⚠️ Tem certeza que deseja fechar este ticket?", view=confirm_view, ephemeral=True)




class ConfirmCloseView(ui.View):
    """Confirmação para fechar o ticket"""
    def __init__(self, bot, open_tickets, channel):
        super().__init__(timeout=30)
        self.bot = bot
        self.open_tickets = open_tickets
        self.channel = channel

    @ui.button(label="✅ Confirmar", style=discord.ButtonStyle.red)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        transcript = await self.create_transcript(self.channel)
        with open(f"transcripts/{self.channel.name}.txt", "w", encoding="utf-8") as f:
            f.write(transcript)
        await self.channel.delete()
        await interaction.response.send_message("✅ Ticket fechado e salvo!", ephemeral=True)

    async def create_transcript(self, channel):
        transcript = ""
        async for message in channel.history(limit=None):
            transcript += f"{message.author.name}: {message.content}\n"
        return transcript


class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.open_tickets = {}

    @commands.command(name="painel_ticket")
    @commands.has_permissions(administrator=True)
    async def painel_ticket(self, ctx):
        embed = discord.Embed(
            title="📩 Sistema de Tickets",
            description="Clique no botão abaixo para abrir um ticket com a equipe!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=TicketButton(self.bot))

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
