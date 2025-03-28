import discord
from discord.ext import commands
from discord.ui import View, Select, Button

class BotConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="configuração")
    @commands.has_permissions(administrator=True)
    async def configuração(self, ctx):
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

        # Criação de uma lista de opções de canais
        channel_select = Select(
            placeholder="Escolha o canal para comandos do bot...",
            options=[discord.SelectOption(label=channel.name, value=str(channel.id)) for channel in ctx.guild.text_channels]
        )

        # Botão para salvar a configuração
        save_button = Button(label="Salvar Configuração", style=discord.ButtonStyle.green)

        # Criando uma View com o Select e o Botão
        view = View()
        view.add_item(channel_select)
        view.add_item(save_button)

        # Enviar a mensagem com o painel configurável
        await ctx.send(embed=embed, view=view)

        # Função de callback para o botão
        async def save_callback(interaction):
            channel_id = channel_select.values[0]
            selected_channel = ctx.guild.get_channel(int(channel_id))

            # Salvar a configuração no banco de dados ou arquivo de configuração
            # Por enquanto, será enviado um feedback sobre a escolha
            await interaction.response.send_message(f"✅ Canal configurado com sucesso! O bot agora responderá apenas no canal: {selected_channel.mention}")

        save_button.callback = save_callback


async def setup(bot):
    await bot.add_cog(BotConfig(bot))
