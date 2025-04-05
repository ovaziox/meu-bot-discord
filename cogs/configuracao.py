import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# Caminhos dos arquivos de dados
PREFIXO_PATH = "data/prefixos.json"
CANAIS_PATH = "data/canais.json"

# Funções utilitárias
def salvar_prefixo(guild_id, novo_prefixo):
    with open(PREFIXO_PATH, "r") as f:
        prefixos = json.load(f)
    prefixos[str(guild_id)] = novo_prefixo
    with open(PREFIXO_PATH, "w") as f:
        json.dump(prefixos, f, indent=4)

def salvar_canais(guild_id, canais_ids):
    with open(CANAIS_PATH, "r") as f:
        canais = json.load(f)
    canais[str(guild_id)] = canais_ids
    with open(CANAIS_PATH, "w") as f:
        json.dump(canais, f, indent=4)

# Modal para alterar prefixo
class MudarPrefixo(discord.ui.Modal, title="Alterar Prefixo"):
    novo_prefixo = discord.ui.TextInput(label="Novo prefixo", placeholder="#", max_length=5)

    async def on_submit(self, interaction: discord.Interaction):
        salvar_prefixo(interaction.guild.id, self.novo_prefixo.value)
        await interaction.response.send_message(
            f"✅ Prefixo alterado para `{self.novo_prefixo.value}`", ephemeral=True
        )

# Menu de seleção de canais
class SelecionarCanais(discord.ui.Select):
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild

        options = [
            discord.SelectOption(label=canal.name, value=str(canal.id))
            for canal in guild.text_channels
        ]

        super().__init__(
            placeholder="Selecione os canais permitidos...",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="select_canais"
        )

    async def callback(self, interaction: discord.Interaction):
        salvar_canais(self.guild.id, self.values)
        canais_mention = ", ".join(f"<#{cid}>" for cid in self.values)
        await interaction.response.send_message(
            f"✅ Canais permitidos atualizados: {canais_mention}", ephemeral=True
        )

# View principal do painel
class ConfiguracaoView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=180)
        self.add_item(SelecionarCanais(bot, guild))
        self.add_item(discord.ui.Button(label="Alterar Prefixo", style=discord.ButtonStyle.primary, custom_id="btn_prefixo"))

    @discord.ui.button(label="Alterar Prefixo", style=discord.ButtonStyle.primary, custom_id="btn_prefixo")
    async def alterar_prefixo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MudarPrefixo())

# Cog com comandos
class Configuracao(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="configuracao")
    async def config_texto(self, ctx):
        """Comando via texto com prefixo"""
        view = ConfiguracaoView(self.bot, ctx.guild)
        await ctx.send("🔧 Painel de configuração:", view=view)

    @app_commands.command(name="configuracao", description="Abra o painel de configuração do bot")
    async def config_slash(self, interaction: discord.Interaction):
        """Comando via slash"""
        view = ConfiguracaoView(self.bot, interaction.guild)
        await interaction.response.send_message("🔧 Painel de configuração:", view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    cog = Configuracao(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.config_slash)
