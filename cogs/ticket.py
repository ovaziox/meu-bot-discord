import discord
from discord.ext import commands
from discord import ui, app_commands
import io

# Mapeamento de descrições para cada tipo de ticket
TICKET_DESCRIPTIONS = {
    "Suporte": "🛠 **Suporte** - Para dúvidas ou problemas com o servidor.",
    "Parceria": "🤝 **Parceria** - Para solicitar parceria com nosso servidor.",
    "Postagem": "📩 **Postagem** - Para enviar uma sugestão de postagem.",
    "Outros": "❓ **Outros** - Para outros tipos de solicitações."
}

class TicketReasonModal(ui.Modal, title="Descreva seu Pedido"):
    def __init__(self, ticket_type: str):
        super().__init__()
        self.ticket_type = ticket_type
        self.add_item(ui.TextInput(label="Explique o motivo do ticket", style=discord.TextStyle.paragraph))

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.ticket_type, self.children[0].value)

class CloseTicketButton(ui.Button):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red)
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        # Verifica se o usuário tem permissão para fechar o ticket
        if interaction.user.guild_permissions.manage_messages or interaction.channel.permissions_for(interaction.user).read_messages:
            # Responde a interação para evitar timeout
            await interaction.response.send_message("Fechando o ticket...", ephemeral=True)
            # Salva a transcrição (apenas em canal de logs)
            await save_transcript(self.channel)
            # Após a transcrição, deleta o canal
            await self.channel.delete()
        else:
            await interaction.response.send_message("❌ Você não tem permissão para fechar este ticket!", ephemeral=True)

class TicketButton(ui.View):
    def __init__(self, ticket_type: str):
        super().__init__(timeout=None)
        self.ticket_type = ticket_type
        self.add_item(OpenTicketButton(ticket_type))

class OpenTicketButton(ui.Button):
    def __init__(self, ticket_type: str):
        super().__init__(label="🎟 Abrir Ticket", style=discord.ButtonStyle.green)
        self.ticket_type = ticket_type

    async def callback(self, interaction: discord.Interaction):
        # Verifica se o usuário já possui um ticket aberto
        open_ticket = discord.utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.name}")
        if open_ticket:
            await interaction.response.send_message("❌ Você já tem um ticket aberto!", ephemeral=True)
            return

        if self.ticket_type == "Outros":
            await interaction.response.send_modal(TicketReasonModal(self.ticket_type))
        else:
            await create_ticket(interaction, self.ticket_type)

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
        ticket_type = self.values[0]
        description = TICKET_DESCRIPTIONS.get(ticket_type, "📌 **Informações sobre o ticket não disponíveis.**")
        embed = discord.Embed(
            title="🎫 Criar um Novo Ticket",
            description=f"{description}\n\nClique no botão abaixo para abrir seu ticket!",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=TicketButton(ticket_type), ephemeral=True)

class TicketMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

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

async def create_ticket(interaction: discord.Interaction, ticket_type: str, reason: str = "N/A"):
    guild = interaction.guild
    category = discord.utils.get(guild.categories, name="Tickets")
    if not category:
        category = await guild.create_category("Tickets")

    ticket_channel = await guild.create_text_channel(
        name=f"ticket-{interaction.user.name}", category=category
    )

    await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
    admin_role = discord.utils.get(guild.roles, permissions=discord.Permissions(administrator=True))
    if admin_role:
        await ticket_channel.set_permissions(admin_role, read_messages=True, send_messages=True)

    embed = discord.Embed(
        title=f"🎟 Novo Ticket - {ticket_type}",
        description=f"Usuário: {interaction.user.mention}\nMotivo: {reason}",
        color=discord.Color.green()
    )

    view = ui.View()
    view.add_item(CloseTicketButton(ticket_channel))

    await ticket_channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"✅ Ticket criado: {ticket_channel.mention}", ephemeral=True)

async def save_transcript(channel: discord.TextChannel):
    messages = await channel.history(limit=1000).flatten()
    transcript = io.StringIO()
    
    for message in reversed(messages):
        transcript.write(f"[{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {message.author}: {message.content}\n")
    
    transcript.seek(0)
    transcript_file = discord.File(transcript, filename=f"transcript-{channel.name}.txt")
    log_channel = discord.utils.get(channel.guild.text_channels, name="logs")
    
    if log_channel:
        await log_channel.send(content=f"📄 Transcript do {channel.name}", file=transcript_file)
    # Removido o envio de transcrição para o próprio canal, pois ele será deletado.

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
    # Sincroniza os comandos slash para garantir que o panelticket seja registrado
    await bot.tree.sync()
