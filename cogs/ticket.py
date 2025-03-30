import discord
from discord.ext import commands
from discord import ui, app_commands

class TicketReasonModal(ui.Modal, title="Descreva seu Pedido"):
    def __init__(self, ticket_type: str):
        super().__init__()
        self.ticket_type = ticket_type
        self.add_item(ui.TextInput(label="Explique o motivo do ticket", style=discord.TextStyle.paragraph))
    
    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")
        
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}", category=category
        )
        
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        
        embed = discord.Embed(
            title=f"🎟 Novo Ticket - {self.ticket_type}",
            description=f"Usuário: {interaction.user.mention}\nMotivo: {self.children[0].value}",
            color=discord.Color.green()
        )
        await ticket_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Ticket criado: {ticket_channel.mention}", ephemeral=True)

class TicketMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class TicketDropdown(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Suporte", description="Ajuda com algo no servidor", emoji="🛠"),
            discord.SelectOption(label="Parceria", description="Solicitar parceria", emoji="🤝"),
            discord.SelectOption(label="Postagem", description="Enviar uma postagem", emoji="📩"),
            discord.SelectOption(label="Outros", description="Outro tipo de solicitação", emoji="❓"),
        ]
        super().__init__(placeholder="Escolha um tipo de ticket...", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketReasonModal(self.values[0]))

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="panelticket", with_app_command=True, description="Envia o painel de tickets")
    @commands.has_permissions(administrator=True)
    async def painel_ticket(self, ctx):
        embed = discord.Embed(
            title="📩 Sistema de Tickets",
            description="Selecione um motivo no menu abaixo para abrir um ticket!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=TicketMenu())

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
