import discord
from discord.ext import commands
from discord import ui
import os

class TicketButton(ui.View):
    """Cria um botão para abrir e fechar tickets"""

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.open_tickets = {}  # Dicionário para armazenar tickets criados

    @ui.button(label="Abrir Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        """Ação ao clicar no botão para abrir um ticket"""
        guild = interaction.guild
        user = interaction.user

        # Nome do canal baseado no usuário
        channel_name = f"ticket-{user.name.lower().replace(' ', '-')}"
        
        # Verifica se já existe um canal de ticket para esse usuário
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message("❌ Você já tem um ticket aberto!", ephemeral=True)
            return
        
        # Criar um novo canal de texto visível apenas para ADMINS e o usuário que abriu
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Todos não podem ver
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            discord.utils.get(guild.roles, permissions=discord.Permissions(administrator=True)): 
                discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        # Criando o canal na categoria "Tickets"
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")  # Cria se não existir

        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        # Armazena o ticket no dicionário (mapeando usuário -> canal)
        self.open_tickets[user.id] = ticket_channel.id

        # Envia mensagem de boas-vindas ao ticket
        await ticket_channel.send(f"🎟️ **Ticket criado por {user.mention}**.\n\nUm administrador responderá em breve!")

        # Adiciona o botão de fechar no canal de ticket
        close_button = CloseTicketButton(self.bot, self.open_tickets)
        await ticket_channel.send("🔒 **Clique no botão abaixo para fechar seu ticket quando o problema for resolvido.**", view=close_button)

        # Resposta ao usuário
        await interaction.response.send_message(f"✅ Seu ticket foi criado: {ticket_channel.mention}", ephemeral=True)


class CloseTicketButton(ui.View):
    """Cria um botão para fechar tickets"""

    def __init__(self, bot, open_tickets):
        super().__init__(timeout=None)
        self.bot = bot
        self.open_tickets = open_tickets  # Passa o dicionário de tickets abertos

    @ui.button(label="Fechar Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        """Ação ao clicar no botão para fechar um ticket"""
        user = interaction.user
        guild = interaction.guild

        # Verifica se o usuário tem um ticket aberto
        if user.id not in self.open_tickets:
            await interaction.response.send_message("❌ Você não tem um ticket aberto!", ephemeral=True)
            return
        
        # Pega o ID do canal que deve ser fechado
        channel_id = self.open_tickets[user.id]
        ticket_channel = guild.get_channel(channel_id)

        if ticket_channel is None:
            await interaction.response.send_message("❌ O ticket já foi fechado ou não existe!", ephemeral=True)
            return

        # Verifica se quem está fechando é o dono do ticket ou um administrador
        if interaction.user.id != user.id and not any(role.permissions.administrator for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas quem abriu o ticket ou um administrador pode fechá-lo!", ephemeral=True)
            return

        # Cria o transcrito
        transcript = await self.create_transcript(ticket_channel)

        # Salva o transcrito em um arquivo
        if not os.path.exists("transcripts"):
            os.makedirs("transcripts")

        with open(f"transcripts/{ticket_channel.name}.txt", "w", encoding="utf-8") as f:
            f.write(transcript)

        # Deleta o canal
        await ticket_channel.delete()

        # Remove o ticket do dicionário
        del self.open_tickets[user.id]

        # Notifica o usuário
        await interaction.response.send_message(f"✅ O ticket foi fechado e transcrito! O transcrito foi salvo como `{ticket_channel.name}.txt`.", ephemeral=True)

    async def create_transcript(self, channel):
        """Cria o transcrito do canal de texto"""
        transcript = ""
        async for message in channel.history(limit=None):  # Pega todas as mensagens do canal
            transcript += f"{message.author.name}: {message.content}\n"
        return transcript


class TicketCog(commands.Cog):
    """Sistema de Tickets"""
    
    def __init__(self, bot):
        self.bot = bot
        self.open_tickets = {}  # Dicionário para armazenar tickets criados

    @commands.command(name="painel_ticket")
    @commands.has_permissions(administrator=True)
    async def painel_ticket(self, ctx):
        """Envia o painel para abrir tickets"""
        embed = discord.Embed(
            title="📩 Suporte via Ticket",
            description="Clique no botão abaixo para abrir um ticket com a equipe!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=TicketButton(self.bot))

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
