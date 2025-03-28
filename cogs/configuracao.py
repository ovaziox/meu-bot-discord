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
        """Comando básico para configurar o bot."""
        
        # Envia um embed com a descrição da configuração
        embed = discord.Embed(
            title="🛠️ Configuração do Bot",
            description="Escolha uma das opções de configuração abaixo:",
            color=discord.Color.green()
        )

        # Opções de configurações
        embed.add_field(
            name="Opções de Configuração",
            value="1️⃣ Escolher canal para comandos do bot\n2️⃣ Configuração do prefixo\n3️⃣ Mensagens de boas-vindas",
            inline=False
        )

        # Criar o painel de opções de configuração
        select_config = Select(
            placeholder="Escolha uma configuração...",
            options=[
                discord.SelectOption(label="Escolher canal para comandos do bot", value="canal_comando"),
                discord.SelectOption(label="Configuração do prefixo", value="prefixo"),
                discord.SelectOption(label="Mensagens de boas-vindas", value="boas_vindas")
            ]
        )
        
        # Botão para salvar a configuração
        save_button = Button(label="Salvar Configuração", style=discord.ButtonStyle.green)

        # Criando a View com o Select e o Botão
        view = View()
        view.add_item(select_config)
        view.add_item(save_button)

        # Envia o painel de configuração
        await ctx.send(embed=embed, view=view)

        # Função de callback para o Select
        async def select_callback(interaction):
            option = select_config.values[0]
            
            # Ações para cada opção escolhida
            if option == "canal_comando":
                await self.configurar_canal(interaction)
            elif option == "prefixo":
                await self.configurar_prefixo(interaction)
            elif option == "boas_vindas":
                await self.configurar_boas_vindas(interaction)

        select_config.callback = select_callback

    async def configurar_canal(self, interaction):
        """Configuração para escolher o canal onde o bot responderá."""
        
        embed = discord.Embed(
            title="Escolha o Canal para Comandos do Bot",
            description="Selecione o canal onde o bot poderá responder aos comandos.",
            color=discord.Color.green()
        )
        
        # Criar o painel com os canais disponíveis
        channel_select = Select(
            placeholder="Escolha o canal para o bot responder...",
            options=[discord.SelectOption(label=channel.name, value=str(channel.id)) for channel in interaction.guild.text_channels]
        )

        save_button = Button(label="Salvar Configuração", style=discord.ButtonStyle.green)

        view = View()
        view.add_item(channel_select)
        view.add_item(save_button)

        await interaction.response.send_message(embed=embed, view=view)

        async def save_callback(interaction):
            channel_id = channel_select.values[0]
            selected_channel = interaction.guild.get_channel(int(channel_id))

            # Salvar a configuração no arquivo
            self.config[str(interaction.guild.id)] = {"canal_id": selected_channel.id}
            self.save_config()

            await interaction.response.send_message(f"✅ Canal configurado com sucesso! O bot agora responderá apenas no canal {selected_channel.mention}")

        save_button.callback = save_callback

    async def configurar_prefixo(self, interaction):
        """Configuração para alterar o prefixo do bot."""
        
        embed = discord.Embed(
            title="Configuração do Prefixo",
            description="Digite o novo prefixo que o bot usará para comandos.",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Aguardar a resposta do usuário com o novo prefixo
        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            new_prefix = msg.content.strip()
            
            # Atualizar e salvar a configuração do prefixo
            self.config[str(interaction.guild.id)]["prefixo"] = new_prefix
            self.save_config()
            
            await interaction.followup.send(f"✅ Prefixo alterado com sucesso! Agora o prefixo é: `{new_prefix}`")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ O tempo para responder expirou. Tente novamente.")

    async def configurar_boas_vindas(self, interaction):
        """Configuração para definir a mensagem de boas-vindas."""
        
        embed = discord.Embed(
            title="Mensagem de Boas-Vindas",
            description="Digite a nova mensagem de boas-vindas para os novos membros.",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Aguardar a resposta do usuário com a nova mensagem
        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            new_message = msg.content.strip()
            
            # Atualizar e salvar a mensagem de boas-vindas
            self.config[str(interaction.guild.id)]["boas_vindas"] = new_message
            self.save_config()
            
            await interaction.followup.send(f"✅ Mensagem de boas-vindas alterada com sucesso! A nova mensagem é: `{new_message}`")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ O tempo para responder expirou. Tente novamente.")

# Função para adicionar o Cog
async def setup(bot):
    await bot.add_cog(BotConfig(bot))
