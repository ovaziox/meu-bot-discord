import discord
import json
from discord.ext import commands
from discord.ui import View, Select, Button

class BotConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Carregar o arquivo de configurações
        self.config_file = "config.json"
        self.load_config()

    def load_config(self):
        """Carregar as configurações do arquivo JSON."""
        try:
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}

    def save_config(self):
        """Salvar as configurações no arquivo JSON."""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    @commands.command(name="configuracao")
    @commands.has_permissions(administrator=True)
    async def configuracao(self, ctx):
        """Comando básico para configurar o canal onde o bot pode responder."""
        
        # Envia um embed com a descrição da configuração
        embed = discord.Embed(
            title="🛠️ Configuração do Bot",
            description="Escolha um canal onde o bot responderá aos comandos.",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Como configurar?",
            value="Escolha um canal de texto onde deseja que o bot responda aos comandos.",
            inline=False
        )

        # Criar o painel com os canais disponíveis
        channel_select = Select(
            placeholder="Escolha o canal para o bot responder...",
            options=[discord.SelectOption(label=channel.name, value=str(channel.id)) for channel in ctx.guild.text_channels]
        )
        
        # Botão para salvar a configuração
        save_button = Button(label="Salvar Configuração", style=discord.ButtonStyle.green)

        # Criando a View com o Select e o Botão
        view = View()
        view.add_item(channel_select)
        view.add_item(save_button)

        # Envia o painel de configuração
        await ctx.send(embed=embed, view=view)

        # Função de callback para o botão
        async def save_callback(interaction):
            channel_id = channel_select.values[0]
            selected_channel = ctx.guild.get_channel(int(channel_id))

            # Salvar a configuração no arquivo
            self.config[str(ctx.guild.id)] = {"canal_id": selected_channel.id}
            self.save_config()

            await interaction.response.send_message(f"✅ Canal configurado com sucesso! O bot agora responderá apenas no canal {selected_channel.mention}")

        save_button.callback = save_callback

    @commands.Cog.listener()
    async def on_message(self, message):
        """Ouvir mensagens e verificar se a mensagem é de um canal autorizado."""
        if message.author.bot:
            return

        # Verificar se o servidor tem uma configuração de canal e se o canal da mensagem está autorizado
        guild_id = str(message.guild.id)
        if guild_id in self.config:
            authorized_channel_id = self.config[guild_id].get("canal_id")
            if str(message.channel.id) != authorized_channel_id:
                return  # Ignorar a mensagem se não for o canal autorizado

        # Se passar na verificação, processa a mensagem normalmente (ex: responder a comandos)
        await self.bot.process_commands(message)


# Função para adicionar o Cog
async def setup(bot):
    await bot.add_cog(BotConfig(bot))
