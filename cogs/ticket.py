import discord
from discord.ext import commands
from discord import ui

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticket_panel")
    @commands.has_permissions(administrator=True)
    async def ticket_panel(self, ctx):
        """Comando para criar o painel de tickets."""
        embed = discord.Embed(
            title="🎫 Sistema de Tickets",
            description="Clique no botão abaixo para abrir um ticket e escolher o motivo.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=TicketButtonView())


class TicketButtonView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="📩 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(
            "Selecione o motivo do ticket abaixo:",
            view=TicketReasonSelectView(),
            ephemeral=True
        )


class TicketReasonSelectView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketReasonSelect())


class TicketReasonSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Suporte", description="Ajuda com problemas técnicos", emoji="🛠️"),
            discord.SelectOption(label="Parceria", description="Solicitação de parceria", emoji="🤝"),
            discord.SelectOption(label="Patrocínio", description="Para negociar patrocínios", emoji="💰"),
            discord.SelectOption(label="Denúncia", description="Reportar comportamento inadequado", emoji="⚠️"),
        ]
        super().__init__(placeholder="Escolha o motivo do ticket...", options=options)

    async def callback(self, interaction: discord.Interaction):
        category = discord.utils.get(interaction.guild.categories, name="Tickets")
        if not category:
            category = await interaction.guild.create_category("Tickets")

        channel_name = f"ticket-{interaction.user.name.lower().replace(' ', '-')}"
        existing_channel = discord.utils.get(interaction.guild.text_channels, name=channel_name)

        if existing_channel:
            await interaction.response.send_message("❌ Você já tem um ticket aberto!", ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            discord.utils.get(interaction.guild.roles, permissions=discord.Permissions(administrator=True)): 
                discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        ticket_channel = await interaction.guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        embed = discord.Embed(
            title="🎟️ Ticket Criado",
            description=f"Olá {interaction.user.mention}, seu ticket foi criado para: **{self.values[0]}**\n\nAguarde a equipe de suporte!\n\n🔒 Clique abaixo para fechar este ticket.",
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
        await interaction.response.defer()
        await self.ticket_channel.delete()
        await interaction.followup.send("✅ Ticket fechado!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
