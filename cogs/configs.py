import discord
from discord.ext import commands
from discord import app_commands
import os  # Para pegar a variável de ambiente do token

# Configuração do bot usando o comando prefixo padrão
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='#', intents=intents)

class BotConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando Slash configurado
    @app_commands.command(name="configuração", description="Configurações do bot")
    async def configuração(self, interaction: discord.Interaction):
        """Comando para configurar o bot em seu servidor."""
        embed = discord.Embed(
            title="🛠️ Configuração do Bot",
            description="Escolha uma das opções abaixo para configurar o bot:",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Configuração do Canal",
            value="Selecione o canal onde o bot pode responder aos comandos.",
            inline=False
        )

        # Opções de canais do servidor para selecionar
        channel_select = discord.ui.Select(
            placeholder="Escolha o canal para comandos do bot...",
            options=[discord.SelectOption(label=channel.name, value=str(channel.id)) for channel in interaction.guild.text_channels]
        )

        # Botão para salvar a configuração
        save_button = discord.ui.Button(label="Salvar Configuração", style=discord.ButtonStyle.green)

        # Função do botão de salvar
        async def save_callback(interaction: discord.Interaction):
            channel_id = channel_select.values[0]
            selected_channel = interaction.guild.get_channel(int(channel_id))

            # Aqui você pode salvar a configuração em algum arquivo ou banco de dados
            await interaction.response.send_message(f"✅ Canal configurado com sucesso! O bot agora responderá apenas no canal: {selected_channel.mention}")

        save_button.callback = save_callback

        # Criação de uma view com o select e o botão
        view = discord.ui.View()
        view.add_item(channel_select)
        view.add_item(save_button)

        # Enviar a mensagem com o painel configurável
        await interaction.response.send_message(embed=embed, view=view)


# Registra o comando slash
@bot.event
async def on_ready():
    print(f'{bot.user} está online e pronto!')

    # Sincroniza os comandos com o servidor
    await bot.tree.sync()

# Adiciona a cog de configurações
async def setup(bot):
    await bot.add_cog(BotConfig(bot))

# Rodando o bot com o token vindo da variável de ambiente
bot.run(os.getenv('DISCORD_TOKEN'))  # 'DISCORD_TOKEN' é a variável de ambiente onde o token está armazenado
