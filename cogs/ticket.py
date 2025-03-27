import discord
from discord.ext import commands
from discord import ui

class TicketView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(TicketReasonSelect(bot))
    
    @ui.button(label="📩 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("❌ Escolha um motivo antes de abrir um ticket!", ephemeral=True)


class TicketReasonSelect(ui.Select):
    def __init__(self, bot):
        options = [
            discord.SelectOption(label="Suporte", description="Problemas técnicos ou dúvidas", emoji="💬"),
            discord.SelectOption(label="Parceria", description="Solicitação de parceria", emoji="🤝"),
            discord.SelectOption(label="Patrocínio", description="Interesse em patrocinar", emoji="💰"),
            discord.SelectOption(label="Denúncia", description="Reportar uma infração", emoji="⚠️")
        ]
        super().__init__(placeholder="Escolha o motivo do ticket...", min_values=1, max_values=1, options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        reason = self.values[0]
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
        
        embed = discord.Embed(
            title="🎟️ Ticket Criado",
            description=f"Olá {user.mention}, seu ticket foi aberto para **{reason}**.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=CloseTicketView(ticket_channel))
        await interaction.response.send_message(f"✅ Seu ticket foi criado: {ticket_channel.mention}", ephemeral=True)


class CloseTicketView(ui.View):
    def __init__(self, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel
    
    @ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await self.ticket_channel.delete()
        await interaction.response.send_message("✅ Ticket fechado!", ephemeral=True)


class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="painel_ticket")
    @commands.has_permissions(administrator=True)
    async def painel_ticket(self, ctx):
        embed = discord.Embed(
            title="📩 Sistema de Tickets",
            description="Escolha um motivo abaixo e clique no botão para abrir seu ticket!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=TicketView(self.bot))

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
