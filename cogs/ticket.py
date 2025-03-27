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

        # Verifica se o usuário já tem um ticket aberto
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message("❌ Você já tem um ticket aberto!", ephemeral=True)
            return

        # Envia o menu de seleção com os motivos
        select_menu = TicketReasonSelect(self.bot, user, interaction)

        await interaction.response.send_message(
            "Escolha o motivo pelo qual você está abrindo o ticket:",
            view=select_menu,
            ephemeral=True
        )


class TicketReasonSelect(ui.Select):
    """Menu de seleção com motivos para abrir um ticket"""
    def __init__(self, bot, user, interaction):
        options = [
            discord.SelectOption(label="Suporte", description="Para problemas com serviços ou funcionalidades", emoji="💬"),
            discord.SelectOption(label="Parceria", description="Para discutir parcerias", emoji="🤝"),
            discord.SelectOption(label="Patrocínio", description="Para negociar patrocínios", emoji="💰"),
            discord.SelectOption(label="Denúncia", description="Para fazer denúncias de comportamento ou outras questões", emoji="⚠️")
        ]
        super().__init__(placeholder="Escolha o motivo do ticket...", min_values=1, max_values=1, options=options)
        self.bot = bot
        self.user = user
        self.interaction = interaction

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        reason = self.values[0]  # Obtém a razão selecionada
        emoji_map = {
            "Suporte": "💬",
            "Parceria": "🤝",
            "Patrocínio": "💰",
            "Denúncia": "⚠️"
        }

        # Nome do canal com base no usuário
        channel_name = f"ticket-{self.user.name.lower().replace(' ', '-')}"

        # Verifica se já existe um ticket aberto
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message("❌ Você já tem um ticket aberto!", ephemeral=True)
            return

        # Definindo permissões para o canal de ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            self.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            discord.utils.get(guild.roles, permissions=discord.Permissions(administrator=True)): 
                discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        # Criar a categoria de "Tickets" se não existir
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        # Cria o canal de texto para o ticket
        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        
        # Envia uma mensagem com o motivo do ticket, agora com emoji e descrição
        embed = discord.Embed(
            title="🎟️ Ticket Criado",
            description=f"Olá {self.user.mention}, você escolheu a opção: {emoji_map[reason]} **{reason}**\n\nUm membro da equipe irá atendê-lo em breve!\n\n🔒 Clique abaixo para fechar este ticket quando o problema for resolvido.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=CloseTicketButton(self.bot, ticket_channel))
        await interaction.followup.send(f"✅ Seu ticket foi criado: {ticket_channel.mention}", ephemeral=True)


class CloseTicketButton(ui.View):
    """Cria um botão para fechar tickets com confirmação"""
    def __init__(self, bot, ticket_channel):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_channel = ticket_channel

    @ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()

        confirm_view = ConfirmCloseView(self.bot, self.ticket_channel)
        await interaction.followup.send("⚠️ Tem certeza que deseja fechar este ticket?", view=confirm_view, ephemeral=True)


class ConfirmCloseView(ui.View):
    """Confirmação para fechar o ticket"""
    def __init__(self, bot, ticket_channel):
        super().__init__(timeout=30)
        self.bot = bot
        self.ticket_channel = ticket_channel

    @ui.button(label="✅ Confirmar", style=discord.ButtonStyle.red)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()

        # Deleta o canal de ticket sem criar transcript
        await self.ticket_channel.delete()

        await interaction.followup.send("✅ Ticket fechado!", ephemeral=True)


class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
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
