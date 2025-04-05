import discord
import json
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select, Button, Modal, TextInput

class Configuracao(commands.Cog):
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

    @app_commands.command(name="configuracao", description="Painel de configuração do bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def configuracao(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛠️ Painel de Configuração",
            description="Escolha uma das opções abaixo para configurar o bot:",
            color=discord.Color.green()
        )

        select_config = Select(
            placeholder="Escolha uma configuração...",
            options=[
                discord.SelectOption(label="Escolher canal para comandos do bot", value="canal_comando"),
                discord.SelectOption(label="Alterar prefixo de comandos", value="prefixo"),
            ]
        )

        view = View()
        view.add_item(select_config)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        async def select_callback(select_interaction: discord.Interaction):
            if select_interaction.user.id != interaction.user.id:
                await select_interaction.response.send_message("❌ Você não pode usar esta interação.", ephemeral=True)
                return

            option = select_config.values[0]
            if option == "canal_comando":
                await self.configurar_canal(select_interaction)
            elif option == "prefixo":
                await self.configurar_prefixo(select_interaction)

        select_config.callback = select_callback

    async def configurar_canal(self, interaction):
        channel_select = Select(
            placeholder="Selecione o canal de comandos do bot",
            options=[
                discord.SelectOption(label=channel.name, value=str(channel.id))
                for channel in interaction.guild.text_channels
            ]
        )

        view = View()
        view.add_item(channel_select)

        await interaction.response.send_message(
            "🗂️ Selecione o canal que o bot usará para comandos:",
            view=view,
            ephemeral=True
        )

        async def select_callback(select_interaction: discord.Interaction):
            if select_interaction.user.id != interaction.user.id:
                await select_interaction.response.send_message("❌ Você não pode usar esta interação.", ephemeral=True)
                return

            canal_id = int(channel_select.values[0])
            guild_id = str(interaction.guild.id)

            if guild_id not in self.config:
                self.config[guild_id] = {}

            self.config[guild_id]["canal_id"] = canal_id
            self.save_config()

            canal = interaction.guild.get_channel(canal_id)
            await select_interaction.response.send_message(f"✅ Canal configurado para {canal.mention} com sucesso!", ephemeral=True)

        channel_select.callback = select_callback

    async def configurar_prefixo(self, interaction):
        class PrefixModal(Modal, title="Alterar Prefixo"):
            novo_prefixo = TextInput(label="Novo prefixo", placeholder="Exemplo: !", max_length=5)

            async def on_submit(self, modal_interaction: discord.Interaction):
                guild_id = str(modal_interaction.guild.id)
                if guild_id not in self.config:
                    self.config[guild_id] = {}

                self.config[guild_id]["prefixo"] = self.novo_prefixo.value.strip()
                self.save_config()

                await modal_interaction.response.send_message(f"✅ Prefixo alterado para `{self.novo_prefixo.value.strip()}` com sucesso!", ephemeral=True)

        await interaction.response.send_modal(PrefixModal())

async def setup(bot):
    await bot.add_cog(Configuracao(bot))
