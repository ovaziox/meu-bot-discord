import discord
from discord.ext import commands

class BotConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            value="Digite o nome do canal onde deseja que o bot responda.",
            inline=False
        )
        
        # Envia a mensagem para o usuário
        await ctx.send(embed=embed)

        # Aguardando a resposta do usuário
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            # Espera a resposta do usuário (nome do canal)
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            channel_name = msg.content.strip()

            # Tenta pegar o canal pelo nome
            channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)

            if channel:
                await ctx.send(f"✅ Canal configurado com sucesso! O bot agora responderá apenas no canal {channel.mention}.")
            else:
                await ctx.send("❌ Canal não encontrado. Certifique-se de digitar o nome corretamente.")
        except Exception as e:
            await ctx.send("❌ Não foi possível configurar o canal. Tente novamente.")

# Função para adicionar o Cog
async def setup(bot):
    await bot.add_cog(BotConfig(bot))
