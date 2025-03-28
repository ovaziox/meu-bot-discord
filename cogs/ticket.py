import discord
from discord.ext import commands
from discord import ui

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="painel_ticket")
    @commands.has_permissions(administrator=True)
    async def painel_ticket(self, ctx):
        embed = discord.Embed(
            title="\U0001F4E9 Sistema de Tickets",
            description="Clique no botão abaixo para abrir um ticket! Você poderá escolher o motivo depois.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=TicketButton(self.bot))

class TicketButton(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="\U0001F4E9 Abrir Ticket", style=discord.ButtonStyle.green)
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(view=TicketMenu(self.bot, interaction.user), ephemeral=True)

class TicketMenu(ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.reason = None

    @ui.select(
        placeholder="Escolha o motivo do ticket...",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Suporte", emoji="\U0001F4AC"),
            discord.SelectOption(label="Parceria", emoji="\U0001F91D"),
            discord.SelectOption(label="Patrocínio", emoji="\U0001F4B0"),
            discord.SelectOption(label="Denúncia", emoji="⚠️"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: ui.Select):
        self.reason = select.values[0]
        await interaction.response.defer()
        await self.create_ticket(interaction)

    async def create_ticket(self, interaction):
        guild = interaction.guild
        user = self.user
        channel_name = f"ticket-{user.name.lower().replace(' ', '-')}"
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)

        if existing_channel:
            await interaction.followup.send("❌ Você já tem um ticket aberto!", ephemeral=True)
            return

        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            discord.utils.get(guild.roles, permissions=discord.Permissions(administrator=True)): 
                discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        embed = discord.Embed(
            title="\U0001F3AB Ticket Criado",
            description=f"Olá {user.mention}, você escolheu: **{self.reason}**\n\nUm membro da equipe irá atendê-lo em breve!",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=CloseTicketButton(self.bot, ticket_channel, user))
        await interaction.followup.send(f"✅ Seu ticket foi criado: {ticket_channel.mention}", ephemeral=True)

class CloseTicketButton(ui.View):
    def __init__(self, bot, ticket_channel, user):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_channel = ticket_channel
        self.user = user

    @ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        transcript = await self.create_transcript(self.ticket_channel)

        try:
            await self.user.send("📜 Aqui está o transcript do seu ticket:", file=discord.File(fp=transcript, filename="transcript.txt"))
        except:
            pass  # Caso o bot não consiga enviar DM
        
        await self.ticket_channel.delete()

    async def create_transcript(self, channel):
        transcript_text = ""
        async for message in channel.history(limit=None, oldest_first=True):
            transcript_text += f"[{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {message.author.name}: {message.content}\n"
        
        transcript_path = f"/tmp/{channel.name}.txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)
        
        return transcript_path

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
