import discord
from discord.ext import commands
from discord import ui, app_commands

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="panelticket", with_app_command=True, description="Envia o painel de tickets")
    @commands.has_permissions(administrator=True)
    async def painel_ticket(self, ctx):
        await self.send_ticket_panel(ctx.channel)
        if isinstance(ctx, discord.Interaction):
            await ctx.followup.send("✅ Painel de tickets enviado!", ephemeral=True)
        else:
            await ctx.send("✅ Painel de tickets enviado!")

    async def send_ticket_panel(self, channel):
        embed = discord.Embed(
            title="📩 Sistema de Tickets",
            description="Selecione um motivo abaixo para abrir um ticket!",
            color=discord.Color.green()
        )
        await channel.send(content="||@everyone||", embed=embed, view=TicketMenu())

class TicketMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class TicketDropdown(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Suporte", description="Precisa de ajuda? Escolha esta opção!"),
            discord.SelectOption(label="Parceria", description="Deseja uma parceria? Escolha esta opção!"),
            discord.SelectOption(label="Postagem", description="Quer divulgar algo? Escolha esta opção!"),
            discord.SelectOption(label="Outros", description="Outro motivo? Escolha esta opção!"),
        ]
        super().__init__(placeholder="Escolha um motivo", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketReasonModal(self.values[0]))

class TicketReasonModal(ui.Modal):
    def __init__(self, motivo):
        super().__init__(title="Motivo do Ticket")
        self.motivo_escolhido = motivo
        self.motivo = ui.TextInput(label="Descreva o motivo do ticket", placeholder="Exemplo: Preciso de suporte técnico.")
        self.add_item(self.motivo)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        reason = self.motivo.value

        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        channel_name = f"ticket-{user.name.lower().replace(' ', '-')}"
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)

        if existing_channel:
            await interaction.response.send_message("❌ Você já tem um ticket aberto!", ephemeral=True)
            return

        staff_role = discord.utils.get(guild.roles, name="Staff")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        embed = discord.Embed(
            title="🎟️ Ticket Criado",
            description=f"Olá {user.mention}, você escolheu: **{self.motivo_escolhido}**\n\nAguarde um membro da equipe!",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=CloseTicketButton(ticket_channel, user))
        await interaction.response.send_message(f"✅ Seu ticket foi criado: {ticket_channel.mention}", ephemeral=True)

class CloseTicketButton(ui.View):
    def __init__(self, ticket_channel, user):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel
        self.user = user

    @ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        transcript = await self.create_transcript(self.ticket_channel)

        try:
            await self.user.send("📜 Aqui está o transcript do seu ticket:", file=discord.File(fp=transcript, filename="transcript.txt"))
        except:
            pass

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
