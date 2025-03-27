import discord
from discord.ext import commands
import json

class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Carrega as configurações do arquivo JSON
        self.config = self.load_config()

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}  # Retorna um dicionário vazio se o arquivo não for encontrado

    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)

    @commands.command(name="set_channels")
    @commands.has_permissions(administrator=True)  # Restringe o comando a administradores
    async def set_channels(self, ctx, command_channel: discord.TextChannel, other_channel: discord.TextChannel = None):
        """Comando para configurar os canais onde o bot poderá executar comandos"""
        if not other_channel:
            other_channel = command_channel  # Se não passar o segundo canal, usa o primeiro como canal secundário

        # Salva as configurações nos canais definidos
        self.config['command_channel'] = command_channel.id
        self.config['other_channel'] = other_channel.id
        self.save_config()

        await ctx.send(f"✅ Comandos agora poderão ser executados apenas nos canais {command_channel.mention} e {other_channel.mention}.")

    @commands.command(name="say")
    async def say(self, ctx, *, message: str):
        """Comando para enviar uma mensagem formatada"""
        # Verifica se o comando foi enviado no canal correto
        if ctx.channel.id not in [self.config.get('command_channel'), self.config.get('other_channel')]:
            await ctx.send("❌ Este comando não pode ser executado neste canal.")
            return

        # Criação do embed
        embed = discord.Embed(
            title="Mensagem do Bot",
            description=message,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Enviado por {ctx.author.name}", icon_url=ctx.guild.icon.url)

        # Envia a mensagem
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotCommands(bot))
