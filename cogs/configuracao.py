import discord
import json
import asyncio
from discord.ext import commands
from discord.ui import View, Select, Button

class BotConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "config.json"
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    @commands.command(name="configuracao")
    @commands.has_permissions(administrator=True)
    async def configuracao(self, ctx):
        embed = discord.Embed(
            title="🛠️ Configuração do Bot",
            description="Escolha uma das opções de configuração abaixo:",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Opções",
            value="🔹 Canal de comandos\n🔹 Prefixo de comandos\n🔹 Mensagem de boas-vindas",
            inline=False
        )

        # Callback do Select
        async def select_callback(interaction: discord.Interaction):
            selected = select.values[0]
            if selected == "canal_comando":
                await self.configurar_canal(interaction)
            elif selected == "prefixo":
                await self.configurar_prefixo(interaction)
            elif selected == "boas_vindas":
                await self.configurar_boas_vindas(interaction)

        # Select de opções
        select = Select(
            placeholder="Escolha uma configuração...",
            options=[
                discord.SelectOption(label="Canal de comandos", value="canal_comando"),
                discord.SelectOption(label="Prefixo de comandos", value="prefixo"),
                discord.SelectOption(label="Mensagem de boas-vindas", value="boas_vindas"),
            ]
        )
        select.callback = select_callback

        view = View()
        view.add_item(select)

        await ctx.send(embed=embed, view=view)

    async def configurar_canal(self, interaction):
        embed = discord.Embed(
            title="📢 Escolher canal para comandos",
            description="Selecione um canal de texto onde o bot poderá responder aos comandos.",
            color=discord.Color.blurple()
        )

        channel_options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in interaction.guild.text_channels[:25]
        ]

        channel_select = Select(
            placeholder="Selecione o canal",
            options=channel_options
        )

        async def canal_callback(interaction2: discord.Interaction):
            canal_id = channel_select.values[0]
            if str(interaction.guild.id) not in self.config:
                self.config[str(interaction.guild.id)] = {}
            self.config[str(interaction.guild.id)]["canal_id"] = int(canal_id)
            self.save_config()

            await interaction2.response.send_message(
                f"✅ Canal configurado para <#{canal_id}> com sucesso!",
                ephemeral=True
            )

        channel_select.callback = canal_callback

        view = View()
        view.add_item(channel_select)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def configurar_prefixo(self, interaction):
        embed = discord.Embed(
            title="🔤 Alterar Prefixo",
            description="Envie o novo prefixo no chat abaixo. Você tem 30 segundos.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            new_prefix = msg.content.strip()

            if str(interaction.guild.id) not in self.config:
                self.config[str(interaction.guild.id)] = {}

            self.config[str(interaction.guild.id)]["prefixo"] = new_prefix
            self.save_config()

            await interaction.followup.send(f"✅ Prefixo atualizado para: `{new_prefix}`", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Tempo esgotado! Tente novamente.", ephemeral=True)

    async def configurar_boas_vindas(self, interaction):
        embed = discord.Embed(
            title="👋 Mensagem de Boas-Vindas",
            description="Digite a mensagem que será enviada quando um novo membro entrar.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            mensagem = msg.content.strip()

            if str(interaction.guild.id) not in self.config:
                self.config[str(interaction.guild.id)] = {}

            self.config[str(interaction.guild.id)]["boas_vindas"] = mensagem
            self.save_config()

            await interaction.followup.send("✅ Mensagem de boas-vindas atualizada!", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Tempo esgotado! Tente novamente.", ephemeral=True)

# Adicionar o cog
async def setup(bot):
    await bot.add_cog(BotConfig(bot))
