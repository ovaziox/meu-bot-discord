import discord
from discord.ext import commands
from discord import app_commands
import json
import os

PREFIXO_PATH = "data/prefixos.json"
CANAIS_PATH = "data/canais.json"

def salvar_json(path, dados):
    with open(path, "w") as f:
        json.dump(dados, f, indent=4)

def carregar_json(path):
    if not os.path.exists(path):
        salvar_json(path, {})
    with open(path, "r") as f:
        return json.load(f)

class ConfigView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=180)
        self.bot = bot
        self.guild = guild

        # Menu de canais
        self.add_item(ChannelSelect(bot, guild))

        # Botão de mudar prefixo
        self.add_item(ChangePrefixButton(bot, guild))

class ChannelSelect(discord.ui.Select):
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        canais = [discord.SelectOption(label=canal.name, value=str(canal.id)) 
                  for canal in guild.text_channels]

        super().__init__(
            placeholder="Selecione os canais permitidos para comandos",
            min_values=1,
            max_values=min(len(canais), 25),
            options=canais
        )

    async def callback(self, interaction: discord.Interaction):
        canais_selecionados = self.values
        canais_data = carregar_json(CANAIS_PATH)
        canais_data[str(self.guild.id)] = canais_selecionados
        salvar_json(CANAIS_PATH, canais_data)
        nomes = [f"<#{cid}>" for cid in canais_selecionados]
        await interaction.response.send_message(
            f"✅ Comandos agora só funcionarão nos canais: {', '.join(nomes)}",
            ephemeral=True
        )

class ChangePrefixButton(discord.ui.Button):
    def __init__(self, bot, guild):
        super().__init__(label="Alterar Prefixo", style=discord.ButtonStyle.primary)
        self.bot = bot
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ChangePrefixModal(self.guild))

class ChangePrefixModal(discord.ui.Modal, title="Alterar Prefixo"):
    novo_prefixo = discord.ui.TextInput(label="Novo prefixo", max_length=5)

    def __init__(self, guild):
        super().__init__()
        self.guild = guild

    async def on_submit(self, interaction: discord.Interaction):
        prefixos = carregar_json(PREFIXO_PATH)
        prefixos[str(self.guild.id)] = self.novo_prefixo.value
        salvar_json(PREFIXO_PATH, prefixos)
        await interaction.response.send_message(
            f"✅ Prefixo alterado para `{self.novo_prefixo.value}` com sucesso!",
            ephemeral=True
        )

class Configuracao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="configuracao", description="Abra o painel de configuração do bot")
    async def configuracao_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "⚙️ Painel de configuração:",
            view=ConfigView(self.bot, interaction.guild),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Configuracao(bot))
